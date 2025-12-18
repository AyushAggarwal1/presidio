#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

import requests

from format_handlers import read_archive_entries, read_supported_text
from metadata.entity_metadata import get_entity_metadata

ANALYZE_URL_DEFAULT = "http://localhost:5002/analyze"
logger = logging.getLogger(__name__)


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
# Output helpers
# ---------------------------------------------------------------------------


def infer_source_type(path: str) -> str:
    """Infer a simple source type from the file extension."""
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    return ext or "text"


def mask_secret(text: str, start: Optional[int], end: Optional[int]) -> str:
    """Return the exact substring for the detected secret span."""
    try:
        if start is None or end is None:
            return ""
        if not isinstance(start, int) or not isinstance(end, int):
            return ""
        if start < 0 or end < 0 or start >= len(text):
            return ""
        end = min(len(text), end)
        if end <= start:
            return ""
        return text[start:end]
    except Exception:  # noqa: BLE001
        return ""


def to_serializable_explanation(expl: Optional[object]) -> Optional[Dict]:
    """Convert AnalysisExplanation (or dict) to a serializable dict."""
    if expl is None:
        return None
    if isinstance(expl, dict):
        return expl
    try:
        return dict(expl.__dict__)
    except Exception:  # noqa: BLE001
        return None


def to_serializable_metadata(meta: Optional[object]) -> Optional[Dict]:
    """Ensure recognition_metadata is a dict if possible."""
    if meta is None:
        return None
    if isinstance(meta, dict):
        return meta
    try:
        return dict(meta)
    except Exception:  # noqa: BLE001
        return None


def make_relative(path: str, base: str) -> str:
    """Return a path relative to base, fallback to original on error."""
    try:
        return os.path.relpath(path, base)
    except Exception:  # noqa: BLE001
        return path


def relativize_results(results: List[Dict], base: str) -> List[str]:
    """Rewrite result['location'] to be relative to base and return locations."""
    locations: List[str] = []
    for res in results:
        if not isinstance(res, dict):
            continue
        loc = res.get("location")
        if isinstance(loc, str):
            rel = make_relative(loc, base)
            res["location"] = rel
            locations.append(rel)
        elif loc is not None:
            locations.append(loc)
    return locations


def build_error_result(location: str, source_type: str, error_message: str) -> Dict:
    """Standard error result block for a single file."""
    return {
        "location": location,
        "source_type": source_type,
        "analysis_summary": {"total_entities_found": 0, "entities_found": []},
        "analysis_results": [],
        "error": error_message,
        "status": "ERROR",
    }


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
    except requests.exceptions.HTTPError as exc:
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", "unknown")
        body = ""
        try:
            body = (response.text or "").strip() if response is not None else ""
        except Exception:  # noqa: BLE001
            body = ""
        logger.error(
            "Analyzer API request failed",
            extra={"status": status, "response_text": body[:2000]},
            exc_info=exc,
        )
        return {"error": f"Analyzer API HTTP {status}: {body or exc}"}
    except requests.exceptions.RequestException as exc:
        logger.error("Analyzer API request failed", exc_info=exc)
        return {"error": f"Analyzer API request failed: {exc}"}


def enrich_results_with_metadata(results: List[Dict]) -> List[Dict]:
    """Attach entity metadata (title, description, severity, etc.) to each result."""
    
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
    source_type = "image"

    if Image is None or ImageAnalyzerEngine is None:
        logger.error("Image dependencies missing")
        return build_error_result(
            path,
            source_type,
            "Image scanning requires 'Pillow' and 'presidio-image-redactor' to be installed.",
        )

    try:
        image = Image.open(path)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to open image", extra={"path": path}, exc_info=exc)
        return build_error_result(path, source_type, f"Failed to open image: {exc}")

    engine = ImageAnalyzerEngine()
    try:
        # Perform OCR + analysis manually so we can surface OCR and decision metadata.
        perform_ocr_kwargs, ocr_threshold = engine._parse_ocr_kwargs(None)
        preprocessed_image, preprocessing_metadata = engine.image_preprocessor.preprocess_image(
            image
        )
        if not isinstance(preprocessing_metadata, dict):
            preprocessing_metadata = {}
        preprocessing_metadata.setdefault(
            "preprocessor", engine.image_preprocessor.__class__.__name__
        )
        preprocessing_metadata.setdefault("applied", True)
        ocr_result = engine.ocr.perform_ocr(preprocessed_image, **perform_ocr_kwargs)
        ocr_result = engine.remove_space_boxes(ocr_result)
        if preprocessing_metadata and ("scale_factor" in preprocessing_metadata):
            ocr_result = engine._scale_bbox_results(
                ocr_result, preprocessing_metadata["scale_factor"]
            )
        if ocr_threshold:
            ocr_result = engine.threshold_ocr_result(ocr_result, ocr_threshold)

        ocr_text = engine.ocr.get_text_from_ocr_dict(ocr_result)
        text_analyzer_kwargs = {"language": language, "return_decision_process": True}
        allow_list = engine._check_for_allow_list(text_analyzer_kwargs)
        analyzer_result = engine.analyzer_engine.analyze(
            text=ocr_text, **text_analyzer_kwargs
        )
        bboxes = engine.map_analyzer_results_to_bounding_boxes(
            analyzer_result, ocr_result, ocr_text, allow_list
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to analyze image", extra={"path": path}, exc_info=exc)
        return build_error_result(path, source_type, f"Failed to analyze image: {exc}")

    analyzer_lookup = {
        (res.entity_type, res.start, res.end): res
        for res in analyzer_result
        if hasattr(res, "entity_type") and hasattr(res, "start") and hasattr(res, "end")
    }

    analysis_results: List[Dict] = []
    for r in bboxes:
        matched = analyzer_lookup.get((r.entity_type, r.start, r.end))
        analysis_results.append(
            {
                "entity_type": r.entity_type,
                "start": r.start,
                "end": r.end,
                "score": r.score,
                "secret_found": mask_secret(ocr_text or "", r.start, r.end),
                "analysis_explanation": to_serializable_explanation(
                    getattr(matched, "analysis_explanation", None)
                ),
                "recognition_metadata": to_serializable_metadata(
                    getattr(matched, "recognition_metadata", None)
                ),
                "left": r.left,
                "top": r.top,
                "width": r.width,
                "height": r.height,
            }
        )

    enriched = enrich_results_with_metadata(analysis_results)
    entity_count, entities_found = summarize_entities(enriched)

    return {
        "location": path,
        "source_type": source_type,
        "analysis_summary": {
            "total_entities_found": entity_count,
            "entities_found": entities_found,
        },
        "source_type_metadata": {
            "ocr_text": ocr_text,
            "preprocessing": preprocessing_metadata,
        },
        "analysis_results": enriched,
    }


def process_text_source(
    path: str,
    text: str,
    language: str,
    analyze_url: str,
    archive_path: Optional[str] = None,
) -> Dict:
    """Process already-extracted text (from any file type)."""
    source_type = infer_source_type(path)
    if not text or not str(text).strip():
        logger.warning("No text content to analyze", extra={"path": path})
        err = build_error_result(path, source_type, "No text content to analyze.")
        if archive_path:
            err["archive_path"] = archive_path
        return err
    analysis = analyze_text(text, language=language, analyze_url=analyze_url)
    if isinstance(analysis, dict) and "error" in analysis:
        logger.error(
            "Analyzer error for text source",
            extra={"path": path, "error": analysis.get("error")},
        )
        err = build_error_result(path, source_type, analysis["error"])
        err["analysis_error"] = analysis
        return err

    if not isinstance(analysis, list):
        # Unexpected format from API
        logger.error("Unexpected analyzer response format", extra={"path": path})
        return build_error_result(path, source_type, "Unexpected analyzer response format.")

    enriched = enrich_results_with_metadata(analysis)

    detections: List[Dict] = []
    for ent in enriched:
        if not isinstance(ent, dict):
            continue
        masked_secret = mask_secret(text or "", ent.get("start"), ent.get("end"))
        detection = {
            "entity_type": ent.get("entity_type"),
            "start": ent.get("start"),
            "end": ent.get("end"),
            "score": ent.get("score"),
            "secret_found": masked_secret,
            "analysis_explanation": ent.get("analysis_explanation"),
            "recognition_metadata": ent.get("recognition_metadata"),
        }
        # Include any additional metadata the enrichment step may have added.
        for key, value in ent.items():
            if key not in detection:
                detection[key] = value
        detections.append(detection)

    entity_count, entities_found = summarize_entities(enriched)

    return {
        "location": path,
        # "archive_path": archive_path,
        "source_type": source_type,
        "source_type_metadata": {},
        "analysis_summary": {
        "total_entities_found": entity_count,
        "entities_found": entities_found,
        },
        "analysis_results": detections,
    }


def _is_archive(path: str) -> bool:
    lower_path = path.lower()
    if lower_path.endswith((".tar.gz", ".tgz")):
        return True
    ext = os.path.splitext(lower_path)[1]
    return ext in {".tar", ".zip"}


def _format_archive_location(archive_path: str, member: str) -> str:
    return f"{archive_path}::{member}"


def process_file(path: str, language: str, analyze_url: str):
    """Detect file type and route to the appropriate processing pipeline."""
    abs_path = os.path.abspath(path)
    logger.info("Processing file %s", abs_path)

    # Images
    if is_image(abs_path):
        return process_image(abs_path, language=language)

    # PDFs
    if is_pdf(abs_path):
        pdf_text, pdf_err = extract_pdf_text(abs_path)
        if pdf_err is not None:
            logger.error("PDF extract failed", extra={"path": abs_path, "error": pdf_err})
            return build_error_result(abs_path, "pdf", pdf_err)
        return process_text_source(
            abs_path,
            text=pdf_text or "",
            language=language,
            analyze_url=analyze_url,
        )

    # Archives with multiple members
    if _is_archive(abs_path):
        entries, archive_err = read_archive_entries(abs_path)
        if archive_err is not None or entries is None:
            logger.error(
                "Archive read failed", extra={"path": abs_path, "error": archive_err}
            )
            return build_error_result(abs_path, "archive", archive_err or "")

        archive_results: List[Dict] = []
        for member_name, member_text in entries:
            member_location = _format_archive_location(abs_path, member_name)
            archive_results.append(
                process_text_source(
                    member_location,
                    text=member_text,
                    language=language,
                    analyze_url=analyze_url,
                    archive_path=abs_path,
                )
            )
        return archive_results

    # Fallback: treat as text (supports multiple formats)
    text, read_err = read_supported_text(abs_path)
    if read_err is not None:
        logger.error("Read text failed", extra={"path": abs_path, "error": read_err})
        return build_error_result(abs_path, infer_source_type(abs_path), read_err)

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
    timestamp = (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    results: List[Dict] = []
    base_dir = abs_path if os.path.isdir(abs_path) else os.path.dirname(abs_path) or abs_path

    if os.path.isfile(abs_path):
        # Single file
        res = process_file(abs_path, language=language, analyze_url=analyze_url)
        if isinstance(res, list):
            results.extend(res)
        else:
            results.append(res)
    elif os.path.isdir(abs_path):
        if recursive:
            walker = os.walk(abs_path)
        else:
            try:
                entries = [os.path.join(abs_path, e) for e in os.listdir(abs_path)]
            except OSError as exc:  # noqa: BLE001
                logger.error("Failed to list directory", extra={"path": abs_path}, exc_info=exc)
                return {
                    "scan_type": "data-security",
                    "timestamp": timestamp,
                    "status": "ERROR",
                    "scan_scope": {
                        "total_locations_scanned": 0,
                        "locations": [],
                    },
                    "summary": {"total_entities_found": 0, "unique_entity_types": []},
                    "results": [],
                    "error": f"Failed to list directory: {exc}",
                }
            walker = [(abs_path, [], [os.path.basename(p) for p in entries if os.path.isfile(p)])]

        for dirpath, _, filenames in walker:
            for name in filenames:
                file_path = os.path.join(dirpath, name)
                res = process_file(file_path, language=language, analyze_url=analyze_url)
                if isinstance(res, list):
                    results.extend(res)
                else:
                    results.append(res)
                logger.debug("File processed", extra={"path": file_path})
    else:
        return {
            "scan_type": "data-security",
            "timestamp": timestamp,
            "status": "ERROR",
            "scan_scope": {"total_locations_scanned": 0, "locations": []},
            "summary": {"total_entities_found": 0, "unique_entity_types": []},
            "results": [],
            "error": f"Path not found or invalid: {abs_path}",
        }

    locations = relativize_results(results, base_dir)
    total_entities = sum(
        r.get("analysis_summary", {}).get("total_entities_found", 0)
        for r in results
        if isinstance(r, dict)
    )
    unique_entity_types: Set[str] = set()
    status = "COMPLETED"
    for r in results:
        if not isinstance(r, dict):
            continue
        entities = r.get("analysis_summary", {}).get("entities_found", [])
        unique_entity_types.update([e for e in entities if e])
        if r.get("status") == "ERROR":
            status = "COMPLETED_WITH_ERRORS"

    if not results:
        status = "NO_FILES_FOUND"

    return {
        "scan_type": "data-security",
        "timestamp": timestamp,
        "status": status,
        "scan_scope": {
            "total_locations_scanned": len(locations),
            "locations": locations,
        },
        "summary": {
            "total_entities_found": total_entities,
            "unique_entity_types": sorted(unique_entity_types),
        },
        "results": results,
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
        help="Recursively scan directories (default: True)",
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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    main()

