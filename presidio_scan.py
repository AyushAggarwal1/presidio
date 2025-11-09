#!/usr/bin/env python3
"""
Consolidated Presidio scanner with JSON output and path filters.

Features:
- Scan a single file or an entire directory (recursive or not)
- JSON output to stdout (or optional --output file)
- Regex-based allow/ignore filters for files and directories
- Uses Presidio API for analyze (http://localhost:5002/analyze)
  and anonymize (http://localhost:5001/anonymize)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Pattern, Sequence, Tuple

import fnmatch
from bisect import bisect_right
import requests

from entity_metadata import get_entity_metadata

ANALYZE_URL_DEFAULT = "http://localhost:5002/analyze"
ANONYMIZE_URL_DEFAULT = "http://localhost:5001/anonymize"


def get_supported_file_extensions() -> List[str]:
    return [
        ".txt",
        ".log",
        ".csv",
        ".json",
        ".md",
        ".py",
        ".js",
        ".html",
        ".xml",
        ".yaml",
        ".yml",
    ]


def is_extension_allowed(file_path: str, allowed_exts: Sequence[str]) -> bool:
    file_path_lower = file_path.lower()
    return any(file_path_lower.endswith(ext.lower()) for ext in allowed_exts)


def compile_patterns(patterns: Optional[Sequence[str]]) -> Tuple[List[Pattern], List[str]]:
    """Compile regex patterns and collect any errors as strings."""
    if not patterns:
        return [], []
    compiled: List[Pattern] = []
    errors: List[str] = []
    for pattern in patterns:
        try:
            compiled.append(re.compile(pattern))
        except re.error as exc:
            errors.append(f"Invalid regex '{pattern}': {exc}")
    return compiled, errors


def path_matches_any(path_str: str, patterns: Iterable[Pattern]) -> bool:
    for pat in patterns:
        if pat.search(path_str):
            return True
    return False


def path_matches_any_glob(path_str: str, patterns: Sequence[str]) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(path_str, pat):
            return True
    return False


def filter_should_include_file(
    file_path: str,
    allow_patterns: Sequence[Pattern],
    ignore_patterns: Sequence[Pattern],
    allow_globs: Sequence[str],
    ignore_globs: Sequence[str],
) -> bool:
    # Ignore always takes precedence
    if path_matches_any(file_path, ignore_patterns) or path_matches_any_glob(file_path, ignore_globs):
        return False
    # If allow list provided, require a match
    has_allow = bool(allow_patterns) or bool(allow_globs)
    if has_allow:
        allow_match = path_matches_any(file_path, allow_patterns) or path_matches_any_glob(
            file_path, allow_globs
        )
        if not allow_match:
            return False
    return True


def walk_files_with_filters(
    root: str,
    recursive: bool,
    allow_patterns: Sequence[Pattern],
    ignore_patterns: Sequence[Pattern],
    allowed_exts: Sequence[str],
    scan_all_text: bool,
    allow_globs: Sequence[str],
    ignore_globs: Sequence[str],
) -> List[str]:
    """
    Walk directory applying directory and file filters via regex on full paths.
    Directories matching ignore_patterns are pruned from traversal.
    """
    matched_files: List[str] = []
    root_path = os.path.abspath(root)

    if not recursive:
        # One level: listdir + filter
        try:
            for entry in os.listdir(root_path):
                abs_path = os.path.join(root_path, entry)
                if not os.path.isfile(abs_path):
                    continue
                if not scan_all_text and not is_extension_allowed(abs_path, allowed_exts):
                    continue
                if filter_should_include_file(
                    abs_path,
                    allow_patterns=allow_patterns,
                    ignore_patterns=ignore_patterns,
                    allow_globs=allow_globs,
                    ignore_globs=ignore_globs,
                ):
                    matched_files.append(abs_path)
        except OSError:
            # If directory not readable, just return empty
            return []
        return matched_files

    # Recursive: prune ignored directories
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Prune ignored directories
        pruned = []
        for d in list(dirnames):
            abs_d = os.path.join(dirpath, d)
            if path_matches_any(abs_d, ignore_patterns):
                pruned.append(d)
        # mutate in-place to prune
        for d in pruned:
            dirnames.remove(d)

        for fname in filenames:
            abs_f = os.path.join(dirpath, fname)
            if not scan_all_text and not is_extension_allowed(abs_f, allowed_exts):
                continue
            if filter_should_include_file(
                abs_f,
                allow_patterns=allow_patterns,
                ignore_patterns=ignore_patterns,
                allow_globs=allow_globs,
                ignore_globs=ignore_globs,
            ):
                matched_files.append(abs_f)

    return matched_files


def analyze_with_api(text: str, language: str, analyze_url: str) -> dict:
    try:
        payload = {"text": text, "language": language, "return_decision_process": True}
        response = requests.post(analyze_url, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        return {"error": f"API request failed: {exc}"}


def anonymize_with_api(text: str, analyzer_results: list, anonymize_url: str) -> dict:
    try:
        payload = {
            "text": text,
            "analyzer_results": analyzer_results,
            "anonymizers": {"DEFAULT": {"type": "replace", "new_value": "[REDACTED]"}},
        }
        response = requests.post(anonymize_url, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        return {"error": f"Anonymization failed: {exc}"}


def read_text_file(file_path: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip(), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read file: {exc}"


def build_line_starts(text: str) -> List[int]:
    """
    Build a list of starting offsets for each line in text.
    Returns 0-based offsets; first entry is always 0.
    """
    starts: List[int] = [0]
    for idx, ch in enumerate(text):
        if ch == "\n":
            starts.append(idx + 1)
    return starts


def offset_to_line_col(line_starts: Sequence[int], offset: int) -> Tuple[int, int]:
    """
    Map a 0-based character offset to 1-based (line, col) using precomputed line starts.
    """
    # Index of the line whose start is <= offset
    line_index = bisect_right(line_starts, offset) - 1
    if line_index < 0:
        line_index = 0
    line_no = line_index + 1
    col_no = (offset - line_starts[line_index]) + 1
    return line_no, col_no


def enrich_entities_with_positions(analysis_results: list, text: str) -> list:
    """
    Add line/column info to each entity based on 'start' and 'end' offsets.
    Returns a new list of entity dicts with added fields:
      - line, col (start position)
      - end_line, end_col (end position)
    """
    if not isinstance(analysis_results, list):
        return analysis_results
    line_starts = build_line_starts(text)
    enriched = []
    for ent in analysis_results:
        if not isinstance(ent, dict):
            enriched.append(ent)
            continue
        start = ent.get("start")
        end = ent.get("end")
        if isinstance(start, int) and isinstance(end, int):
            line, col = offset_to_line_col(line_starts, start)
            end_line, end_col = offset_to_line_col(line_starts, max(end - 1, start))
            ent_with_pos = dict(ent)
            ent_with_pos["line"] = line
            ent_with_pos["col"] = col
            ent_with_pos["end_line"] = end_line
            ent_with_pos["end_col"] = end_col
            enriched.append(ent_with_pos)
        else:
            enriched.append(ent)
    return enriched


def enrich_entities_with_metadata(analysis_results: list) -> list:
    """
    Add metadata (title, description, category, domain, severity, recommended_action, link)
    to each entity under the 'metadata' key, based on entity_type.
    """
    if not isinstance(analysis_results, list):
        return analysis_results
    enriched = []
    for ent in analysis_results:
        if not isinstance(ent, dict):
            enriched.append(ent)
            continue
        ent_with_meta = dict(ent)
        entity_type = ent_with_meta.get("entity_type")
        ent_with_meta["metadata"] = get_entity_metadata(entity_type)
        enriched.append(ent_with_meta)
    return enriched


def process_file(
    file_path: str,
    language: str,
    analyze_url: str,
    anonymize_url: str,
) -> dict:
    text, read_err = read_text_file(file_path)
    if read_err is not None:
        return {
            "file_path": file_path,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": read_err,
        }

    analysis_results = analyze_with_api(text, language=language, analyze_url=analyze_url)
    if isinstance(analysis_results, dict) and "error" in analysis_results:
        return {
            "file_path": file_path,
            "timestamp": datetime.now().isoformat(),
            "input_text": text,
            "analysis_error": analysis_results,
            "anonymized_result": {},
            "entity_count": 0,
            "entities_found": [],
            "status": "analyze_error",
        }

    # Enrich entities with line/column positions
    analysis_results_with_positions = enrich_entities_with_positions(analysis_results, text)
    # Attach entity metadata
    analysis_results_with_positions = enrich_entities_with_metadata(analysis_results_with_positions)

    anonymized_results = anonymize_with_api(
        text, analyzer_results=analysis_results, anonymize_url=anonymize_url
    )

    entity_count = len(analysis_results) if isinstance(analysis_results, list) else 0
    entities_found = (
        [e.get("entity_type") for e in analysis_results if isinstance(e, dict)]
        if isinstance(analysis_results, list)
        else []
    )

    return {
        "file_path": file_path,
        "timestamp": datetime.now().isoformat(),
        "input_text": text,
        "analysis_results_with_positions": analysis_results_with_positions,
        "anonymized_result": anonymized_results,
        "entity_count": entity_count,
        "entities_found": entities_found,
        "status": "success",
    }


def process_path(
    path: str,
    recursive: bool,
    allow_patterns: Sequence[Pattern],
    ignore_patterns: Sequence[Pattern],
    language: str,
    analyze_url: str,
    anonymize_url: str,
    allowed_exts: Sequence[str],
    scan_all_text: bool,
    allow_globs: Sequence[str],
    ignore_globs: Sequence[str],
) -> dict:
    abs_path = os.path.abspath(path)
    ts = datetime.now().isoformat()

    if os.path.isfile(abs_path):
        # Apply filters on single file too
        if not scan_all_text and not is_extension_allowed(abs_path, allowed_exts):
            return {
                "file_path": abs_path,
                "timestamp": ts,
                "status": "unsupported_file_type",
            }
        if not filter_should_include_file(
            abs_path,
            allow_patterns=allow_patterns,
            ignore_patterns=ignore_patterns,
            allow_globs=allow_globs,
            ignore_globs=ignore_globs,
        ):
            return {
                "file_path": abs_path,
                "timestamp": ts,
                "status": "skipped_by_filter",
            }
        return process_file(
            abs_path, language=language, analyze_url=analyze_url, anonymize_url=anonymize_url
        )

    if os.path.isdir(abs_path):
        files = walk_files_with_filters(
            abs_path,
            recursive=recursive,
            allow_patterns=allow_patterns,
            ignore_patterns=ignore_patterns,
            allowed_exts=allowed_exts,
            scan_all_text=scan_all_text,
            allow_globs=allow_globs,
            ignore_globs=ignore_globs,
        )
        results = []
        total_entities = 0
        for file_path in files:
            print(f"Processing: {file_path}", file=sys.stderr)
            result = process_file(
                file_path, language=language, analyze_url=analyze_url, anonymize_url=anonymize_url
            )
            results.append(result)
            if "entity_count" in result and isinstance(result["entity_count"], int):
                total_entities += result["entity_count"]

        return {
            "directory_path": abs_path,
            "timestamp": ts,
            "files_processed": len(files),
            "files_found": len(files),
            "total_entities_found": total_entities,
            "recursive_scan": recursive,
            "results": results,
            "status": "success" if files else "no_files_found",
        }

    return {"error": f"Path not found or invalid: {abs_path}", "timestamp": ts, "status": "error"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Presidio scanner with JSON output and allow/ignore regex filters."
    )
    parser.add_argument(
        "path",
        help="File or directory to scan",
    )
    parser.add_argument(
        "--recursive",
        dest="recursive",
        action="store_true",
        default=True,
        help="Recurse into subdirectories (default: True)",
    )
    parser.add_argument(
        "--no-recursive",
        dest="recursive",
        action="store_false",
        help="Do not recurse into subdirectories",
    )
    parser.add_argument(
        "--allow-regex",
        action="append",
        default=[],
        help="Regex for allowed file/directory paths (can be passed multiple times)",
    )
    parser.add_argument(
        "--ignore-regex",
        action="append",
        default=[],
        help="Regex for ignored file/directory paths (can be passed multiple times)",
    )
    parser.add_argument(
        "--allow-glob",
        action="append",
        default=[],
        help="Shell glob for allowed paths (e.g., '**/src/**', '*.json'). Can be repeated.",
    )
    parser.add_argument(
        "--ignore-glob",
        action="append",
        default=[],
        help="Shell glob for ignored paths (e.g., '**/node_modules/**', '*.min.js'). Can be repeated.",
    )
    parser.add_argument(
        "--ext",
        action="append",
        default=[],
        help="Additional file extension to include (e.g., --ext .java). Can be repeated.",
    )
    parser.add_argument(
        "--scan-all-text",
        action="store_true",
        default=False,
        help="Ignore extension allowlist and try to scan any file readable as UTF-8.",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Language for Presidio analyzer (default: en)",
    )
    parser.add_argument(
        "--analyze-url",
        default=ANALYZE_URL_DEFAULT,
        help=f"Presidio analyze endpoint (default: {ANALYZE_URL_DEFAULT})",
    )
    parser.add_argument(
        "--anonymize-url",
        default=ANONYMIZE_URL_DEFAULT,
        help=f"Presidio anonymize endpoint (default: {ANONYMIZE_URL_DEFAULT})",
    )
    parser.add_argument(
        "--output",
        help="Write JSON result to this file instead of stdout",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Compile patterns and capture compilation errors
    allow_patterns, allow_errors = compile_patterns(args.allow_regex)
    ignore_patterns, ignore_errors = compile_patterns(args.ignore_regex)
    pattern_errors = allow_errors + ignore_errors

    if pattern_errors:
        error_json = {
            "timestamp": datetime.now().isoformat(),
            "status": "regex_error",
            "errors": pattern_errors,
        }
        json_str = json.dumps(error_json, indent=2)
        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(json_str + "\n")
            except Exception as exc:  # noqa: BLE001
                print(f"Failed to write output file: {exc}", file=sys.stderr)
                print(json_str)
            return
        print(json_str)
        return

    # Compute effective allowed extensions
    default_exts = get_supported_file_extensions()
    user_exts = [e if e.startswith(".") else f".{e}" for e in (args.ext or [])]
    # Preserve order: defaults first, then user-provided, without duplicates
    seen = set()
    effective_exts: List[str] = []
    for ext in default_exts + user_exts:
        ext_lower = ext.lower()
        if ext_lower not in seen:
            seen.add(ext_lower)
            effective_exts.append(ext_lower)

    result = process_path(
        path=args.path,
        recursive=bool(args.recursive),
        allow_patterns=allow_patterns,
        ignore_patterns=ignore_patterns,
        language=args.language,
        analyze_url=args.analyze_url,
        anonymize_url=args.anonymize_url,
        allowed_exts=effective_exts,
        scan_all_text=bool(args.scan_all_text),
        allow_globs=args.allow_glob or [],
        ignore_globs=args.ignore_glob or [],
    )

    # Attach filter metadata for traceability when directory scanning
    if isinstance(result, dict) and "results" in result:
        result["filters"] = {
            "allow_regex": args.allow_regex or [],
            "ignore_regex": args.ignore_regex or [],
            "allow_glob": args.allow_glob or [],
            "ignore_glob": args.ignore_glob or [],
            "extensions_used": effective_exts,
            "scan_all_text": bool(args.scan_all_text),
        }

    json_str = json.dumps(result, indent=2)
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_str + "\n")
        except Exception as exc:  # noqa: BLE001
            print(f"Failed to write output file: {exc}", file=sys.stderr)
            print(json_str)
        return
    print(json_str)


if __name__ == "__main__":
    main()


