#!/usr/bin/env python3

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests

from metadata.entity_metadata import get_entity_metadata

ANALYZE_URL_DEFAULT = "http://localhost:5002/analyze"


# Optional dependencies
try:
    import PyPDF2  # type: ignore[import]
except Exception:  # noqa: BLE001
    PyPDF2 = None  # type: ignore[assignment]

try:
    from PIL import Image, UnidentifiedImageError
except Exception:  # noqa: BLE001
    Image = None  # type: ignore[assignment]

    class UnidentifiedImageError(Exception):  # type: ignore[no-redef]
        """Fallback if Pillow is not installed."""

        pass

try:
    from presidio_image_redactor import ImageAnalyzerEngine
except Exception:  # noqa: BLE001
    ImageAnalyzerEngine = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Helpers for file type detection and reading
# ---------------------------------------------------------------------------


def is_pdf(path: str) -> bool:
    return path.lower().endswith(".pdf")


def is_image(path: str) -> bool:
    if Image is None:
        return False
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except (UnidentifiedImageError, OSError):  # type: ignore[arg-type]
        return False


def read_text_file(path: str) -> Tuple[Optional[str], Optional[str]]:
    """Read a file as UTF‑8 text."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read(), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read file as UTF-8 text: {exc}"


def extract_pdf_text(path: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract text from PDF using PyPDF2, if available."""
    if PyPDF2 is None:
        return None, (
            "PDF support requires 'PyPDF2' to be installed in this environment."
        )
    try:
        text_chunks: List[str] = []
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)  # type: ignore[attr-defined]
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text_chunks.append(page_text)
        text = "\n".join(text_chunks).strip()
        if not text:
            return None, "No extractable text found in PDF."
        return text, None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to extract text from PDF: {exc}"


# ---------------------------------------------------------------------------
# Presidio analyzer helpers
# ---------------------------------------------------------------------------


def analyze_text(text: str, language: str, analyze_url: str) -> Dict:
    """Call Presidio analyzer API and return the JSON response or an error dict."""
    try:
        payload = {"text": text, "language": language, "return_decision_process": True}
        resp = requests.post(analyze_url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as exc:
        return {"error": f"Analyzer API request failed: {exc}"}


def enrich_results_with_metadata(results: List[Dict]) -> List[Dict]:
    """Attach entity metadata (title, description, severity, etc.) to each result."""
    # 
    # @ayushaggarwal1: used to enrich the results with metadata.(entity_metadata.py)
    # enriched: List[Dict] = []
    # for ent in results:
    #     if not isinstance(ent, dict):
    #         enriched.append(ent)
    #         continue
    #     e = dict(ent)
    #     entity_type = e.get("entity_type") or ""
    #     meta = get_entity_metadata(entity_type)
    #     e.update(meta)
    #     enriched.append(e)
    # return enriched

    return results


def summarize_entities(results: List[Dict]) -> Tuple[int, List[str]]:
    if not isinstance(results, list):
        return 0, []
    entity_types = [r.get("entity_type") for r in results if isinstance(r, dict)]
    return len(results), sorted(set(t for t in entity_types if t))


# ---------------------------------------------------------------------------
# Per-file processing
# ---------------------------------------------------------------------------


def process_image(path: str, language: str) -> Dict:
    """Process an image file using OCR + Presidio image analyzer."""
    if Image is None or ImageAnalyzerEngine is None:
        return {
            "file_path": path,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": (
                "Image scanning requires 'Pillow' and 'presidio-image-redactor' "
                "to be installed."
            ),
        }

    try:
        image = Image.open(path)
    except Exception as exc:  # noqa: BLE001
        return {
            "file_path": path,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": f"Failed to open image: {exc}",
        }

    engine = ImageAnalyzerEngine()
    try:
        bboxes = engine.analyze(image=image, language=language)
    except Exception as exc:  # noqa: BLE001
        return {
            "file_path": path,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": f"Failed to analyze image: {exc}",
        }

    raw_results = [
        {
            "entity_type": r.entity_type,
            "start": r.start,
            "end": r.end,
            "score": r.score,
            "left": r.left,
            "top": r.top,
            "width": r.width,
            "height": r.height,
        }
        for r in bboxes
    ]
    enriched = enrich_results_with_metadata(raw_results)
    entity_count, entities_found = summarize_entities(enriched)

    return {
        "file_path": path,
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "source_type": "image",
        "analysis_results": enriched,
        "entity_count": entity_count,
        "entities_found": entities_found,
    }


def process_text_source(
    path: str, text: str, language: str, analyze_url: str
) -> Dict:
    """Process already-extracted text (from any file type)."""
    analysis = analyze_text(text, language=language, analyze_url=analyze_url)
    if isinstance(analysis, dict) and "error" in analysis:
        return {
            "file_path": path,
            "timestamp": datetime.now().isoformat(),
            "status": "analyze_error",
            "input_text": text,
            "analysis_error": analysis,
            "analysis_results": [],
            "entity_count": 0,
            "entities_found": [],
        }

    if not isinstance(analysis, list):
        # Unexpected format from API
        return {
            "file_path": path,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "input_text": text,
            "error": "Unexpected analyzer response format.",
        }

    enriched = enrich_results_with_metadata(analysis)
    entity_count, entities_found = summarize_entities(enriched)

    return {
        "file_path": path,
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "source_type": "text",
        "input_text": text,
        "analysis_results": enriched,
        "entity_count": entity_count,
        "entities_found": entities_found,
    }


def process_file(path: str, language: str, analyze_url: str) -> Dict:
    """Detect file type and route to the appropriate processing pipeline."""
    abs_path = os.path.abspath(path)

    # Images
    if is_image(abs_path):
        return process_image(abs_path, language=language)

    # PDFs
    if is_pdf(abs_path):
        pdf_text, pdf_err = extract_pdf_text(abs_path)
        if pdf_err is not None:
            return {
                "file_path": abs_path,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": pdf_err,
            }
        return process_text_source(
            abs_path,
            text=pdf_text or "",
            language=language,
            analyze_url=analyze_url,
        )

    # Fallback: treat as text
    text, read_err = read_text_file(abs_path)
    if read_err is not None:
        return {
            "file_path": abs_path,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": read_err,
        }

    return process_text_source(
        abs_path,
        text=text or "",
        language=language,
        analyze_url=analyze_url,
    )


# ---------------------------------------------------------------------------
# Directory scanning
# ---------------------------------------------------------------------------


def scan_path(path: str, recursive: bool, language: str, analyze_url: str) -> Dict:
    abs_path = os.path.abspath(path)

    if os.path.isfile(abs_path):
        # Single file
        return process_file(abs_path, language=language, analyze_url=analyze_url)

    if os.path.isdir(abs_path):
        results: List[Dict] = []
        total_entities = 0
        files_processed = 0

        if recursive:
            walker = os.walk(abs_path)
        else:
            # Single-level directory
            try:
                entries = [os.path.join(abs_path, e) for e in os.listdir(abs_path)]
            except OSError as exc:  # noqa: BLE001
                return {
                    "directory_path": abs_path,
                    "timestamp": datetime.now().isoformat(),
                    "status": "error",
                    "error": f"Failed to list directory: {exc}",
                }
            walker = [(abs_path, [], [os.path.basename(p) for p in entries if os.path.isfile(p)])]

        for dirpath, _, filenames in walker:
            for name in filenames:
                file_path = os.path.join(dirpath, name)
                res = process_file(file_path, language=language, analyze_url=analyze_url)
                results.append(res)
                files_processed += 1
                if isinstance(res, dict) and isinstance(res.get("entity_count"), int):
                    total_entities += int(res["entity_count"])

        return {
            "directory_path": abs_path,
            "timestamp": datetime.now().isoformat(),
            "status": "success" if files_processed else "no_files_found",
            "recursive_scan": recursive,
            "files_processed": files_processed,
            "total_entities_found": total_entities,
            "results": results,
        }

    return {
        "timestamp": datetime.now().isoformat(),
        "status": "error",
        "error": f"Path not found or invalid: {abs_path}",
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Presidio scanner: scan a file or directory and output JSON results."
    )
    parser.add_argument(
        "path",
        help="File or directory to scan",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="Recursively scan directories (default: False)",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Language for Presidio analyzer (default: en)",
    )
    parser.add_argument(
        "--analyze-url",
        default=ANALYZE_URL_DEFAULT,
        help=f"Presidio analyzer endpoint (default: {ANALYZE_URL_DEFAULT})",
    )
    parser.add_argument(
        "--output",
        help="Write JSON result to this file instead of stdout",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = scan_path(
        path=args.path,
        recursive=bool(args.recursive),
        language=args.language,
        analyze_url=args.analyze_url,
    )

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

