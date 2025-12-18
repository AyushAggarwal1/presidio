"""Helpers to extract text from multiple file formats for presidio-scan."""

from __future__ import annotations

import bz2
import csv
import gzip
import json
import os
import tarfile
import zipfile
from typing import Callable, Optional, Tuple

# Optional dependencies
try:
    from docx import Document
except Exception:  # noqa: BLE001
    Document = None  # type: ignore[assignment]

try:
    import openpyxl
except Exception:  # noqa: BLE001
    openpyxl = None  # type: ignore[assignment]

try:
    import xlrd  # type: ignore[import]
except Exception:  # noqa: BLE001
    xlrd = None  # type: ignore[assignment]

try:
    from pptx import Presentation
except Exception:  # noqa: BLE001
    Presentation = None  # type: ignore[assignment]

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
    import yaml  # type: ignore[import]
except Exception:  # noqa: BLE001
    yaml = None  # type: ignore[assignment]


TextResult = Tuple[Optional[str], Optional[str]]
ArchiveEntriesResult = Tuple[Optional[list[Tuple[str, str]]], Optional[str]]


def _read_utf8_text(path: str) -> TextResult:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read(), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read file as UTF-8 text: {exc}"


def _read_compressed(path: str, opener: Callable) -> TextResult:
    try:
        with opener(path, "rb") as f:
            data = f.read()
        return data.decode("utf-8", errors="replace"), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read compressed file: {exc}"


def _read_json_like(path: str) -> TextResult:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        try:
            parsed = json.loads(content)
            pretty = json.dumps(parsed, indent=2)
            return pretty, None
        except Exception:
            # Not valid JSON, but still return raw text to scan.
            return content, None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read JSON file: {exc}"


def _read_jsonl(path: str) -> TextResult:
    """Read JSON Lines/NDJSON; pretty-print each JSON object when possible."""
    try:
        rendered_lines = []
        with open(path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    obj = json.loads(stripped)
                    rendered_lines.append(json.dumps(obj, indent=2))
                except Exception:
                    rendered_lines.append(stripped)
        return "\n".join(rendered_lines), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read JSONL/NDJSON file: {exc}"


def _read_yaml(path: str) -> TextResult:
    if yaml is None:
        return None, "YAML support requires 'pyyaml' to be installed."
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        try:
            parsed = yaml.safe_load(content)
            return yaml.safe_dump(parsed, sort_keys=False), None  # type: ignore[arg-type]
        except Exception:
            # Not strictly valid YAML; return raw text.
            return content, None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read YAML file: {exc}"


def _read_csv_tsv(path: str, delimiter: str) -> TextResult:
    try:
        rows = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                rows.append(delimiter.join(row))
        return "\n".join(rows), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read delimited file: {exc}"


def _read_docx(path: str) -> TextResult:
    if Document is None:
        return None, "DOCX support requires 'python-docx' to be installed."
    try:
        doc = Document(path)  # type: ignore[operator]
        paragraphs = [p.text for p in doc.paragraphs if p.text]
        return "\n".join(paragraphs), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read DOCX file: {exc}"


def _read_xlsx(path: str) -> TextResult:
    if openpyxl is None:
        return None, "XLSX support requires 'openpyxl' to be installed."
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)  # type: ignore[attr-defined]
        chunks = []
        for sheet in wb.worksheets:
            chunks.append(f"# Sheet: {sheet.title}")
            for row in sheet.iter_rows(values_only=True):
                cells = ["" if cell is None else str(cell) for cell in row]
                chunks.append("\t".join(cells))
        wb.close()
        return "\n".join(chunks), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read XLSX file: {exc}"


def _read_xls(path: str) -> TextResult:
    if xlrd is None:
        return None, "XLS support requires 'xlrd' to be installed."
    try:
        book = xlrd.open_workbook(path)  # type: ignore[call-arg]
        chunks = []
        for sheet in book.sheets():
            chunks.append(f"# Sheet: {sheet.name}")
            for row_idx in range(sheet.nrows):
                row = sheet.row_values(row_idx)
                cells = ["" if cell is None else str(cell) for cell in row]
                chunks.append("\t".join(cells))
        return "\n".join(chunks), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read XLS file: {exc}"


def _read_ppt(path: str) -> TextResult:
    if Presentation is None:
        return None, "PPT support requires 'python-pptx' to be installed."
    try:
        pres = Presentation(path)  # type: ignore[operator]
        chunks = []
        for idx, slide in enumerate(pres.slides, start=1):
            chunks.append(f"# Slide {idx}")
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text:
                    chunks.append(shape.text)
        return "\n".join(chunks), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read PPT/PPTX file: {exc}"


def _read_pdf(path: str) -> TextResult:
    if PyPDF2 is None:
        return None, "PDF support requires 'PyPDF2' to be installed."
    try:
        text_chunks = []
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


def _read_image(path: str) -> TextResult:
    if Image is None:
        return None, "Image support requires 'Pillow' to be installed."
    try:
        with Image.open(path) as img:
            img.verify()
        return None, "Image content requires OCR; use image analyzer pipeline."
    except (UnidentifiedImageError, OSError) as exc:  # type: ignore[arg-type]
        return None, f"Failed to open image: {exc}"
    except Exception as exc:  # noqa: BLE001
        return None, f"Image handling error: {exc}"


def _read_zip(path: str) -> TextResult:
    try:
        chunks = []
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                try:
                    with zf.open(info) as f:
                        data = f.read()
                        text = data.decode("utf-8", errors="replace")
                        chunks.append(f"# {info.filename}")
                        chunks.append(text)
                except Exception:
                    # Skip entries we cannot read; continue with others.
                    continue
        if not chunks:
            return None, "No readable text entries found in ZIP."
        return "\n".join(chunks), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read ZIP file: {exc}"


def _read_tar(path: str) -> TextResult:
    try:
        chunks = []
        with tarfile.open(path, "r:*") as tf:
            for member in tf.getmembers():
                if not member.isfile():
                    continue
                try:
                    extracted = tf.extractfile(member)
                    if extracted is None:
                        continue
                    data = extracted.read()
                    text = data.decode("utf-8", errors="replace")
                    chunks.append(f"# {member.name}")
                    chunks.append(text)
                except Exception:
                    # Skip entries we cannot read; continue with others.
                    continue
        if not chunks:
            return None, "No readable text entries found in TAR archive."
        return "\n".join(chunks), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read TAR file: {exc}"


def _read_zip_entries(path: str) -> ArchiveEntriesResult:
    """Return per-entry text for ZIP archives."""
    try:
        entries: list[Tuple[str, str]] = []
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                try:
                    with zf.open(info) as f:
                        data = f.read()
                        text = data.decode("utf-8", errors="replace")
                        entries.append((info.filename, text))
                except Exception:
                    # Skip unreadable members; continue to the next.
                    continue
        if not entries:
            return None, "No readable text entries found in ZIP."
        return entries, None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read ZIP file: {exc}"


def _read_tar_entries(path: str) -> ArchiveEntriesResult:
    """Return per-entry text for TAR/TGZ archives."""
    try:
        entries: list[Tuple[str, str]] = []
        with tarfile.open(path, "r:*") as tf:
            for member in tf.getmembers():
                if not member.isfile():
                    continue
                try:
                    extracted = tf.extractfile(member)
                    if extracted is None:
                        continue
                    try:
                        data = extracted.read()
                        text = data.decode("utf-8", errors="replace")
                        entries.append((member.name, text))
                    finally:
                        extracted.close()
                except Exception:
                    # Skip unreadable members; continue to the next.
                    continue
        if not entries:
            return None, "No readable text entries found in TAR archive."
        return entries, None
    except Exception as exc:  # noqa: BLE001
        return None, f"Failed to read TAR file: {exc}"


def read_archive_entries(path: str) -> ArchiveEntriesResult:
    """Read supported archive formats and return per-member text.

    The outer archive path is not included in the member names; callers can
    combine them to form a fully qualified location.
    """
    lower_path = path.lower()
    if lower_path.endswith((".tar.gz", ".tgz", ".tar")):
        return _read_tar_entries(path)

    ext = os.path.splitext(lower_path)[1]
    if ext == ".zip":
        return _read_zip_entries(path)

    return None, "Unsupported archive type for per-member reading."


def read_supported_text(path: str) -> TextResult:
    """Read content from supported formats as UTF-8 text."""
    lower_path = path.lower()

    # Special handling for compressed tarballs before simple extension parsing.
    if lower_path.endswith((".tar.gz", ".tgz")):
        return _read_tar(path)

    ext = os.path.splitext(path)[1].lower()
    handlers = {
        ".bz2": lambda p: _read_compressed(p, bz2.open),
        ".gz": lambda p: _read_compressed(p, gzip.open),
        ".gzip": lambda p: _read_compressed(p, gzip.open),
        ".csv": lambda p: _read_csv_tsv(p, delimiter=","),
        ".tsv": lambda p: _read_csv_tsv(p, delimiter="\t"),
        ".json": _read_json_like,
        ".jsonl": _read_jsonl,
        ".ndjson": _read_jsonl,
        ".tfstate": _read_json_like,
        ".yaml": _read_yaml,
        ".yml": _read_yaml,
        ".docx": _read_docx,
        ".xlsx": _read_xlsx,
        ".xls": _read_xls,
        ".xml": _read_utf8_text,
        ".sql": _read_utf8_text,
        ".dump": _read_utf8_text,
        ".bak": _read_utf8_text,
        ".env": _read_utf8_text,
        ".log": _read_utf8_text,
        ".txt": _read_utf8_text,
        ".ppt": _read_ppt,
        ".pptx": _read_ppt,
        ".pdf": _read_pdf,
        ".png": _read_image,
        ".jpg": _read_image,
        ".jpeg": _read_image,
        ".bmp": _read_image,
        ".gif": _read_image,
        ".tif": _read_image,
        ".tiff": _read_image,
        ".zip": _read_zip,
        ".tar": _read_tar,
        # ".ps1": _read_utf8_text,
        # ".sh": _read_utf8_text,
        # ".html": _read_utf8_text,
    }

    handler = handlers.get(ext)
    if handler is not None:
        return handler(path)

    # Fallback to plain text for unknown extensions.
    return _read_utf8_text(path)
