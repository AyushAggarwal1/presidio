# File Extension Supported

`presidio-scan` routes files to readers based on extension (case-insensitive). Archives are scanned per member; other files are read as UTF-8 text where applicable.

## Supported formats

| Extensions | Handling | Notes |
| --- | --- | --- |
| `.tar.gz`, `.tgz`, `.tar` | Archive (per-member) | Each member scanned separately; location uses `archive_path::member`. |
| `.zip` | Archive (per-member) | Each member scanned separately; location uses `archive_path::member`. |
| `.bz2`, `.gz`, `.gzip` | Single-file compression | Decompressed then decoded as UTF-8 (errors replaced). |
| `.csv`, `.tsv` | Delimited text | Rows joined with delimiter. |
| `.json`, `.tfstate` | JSON-ish | Pretty-printed if valid JSON; otherwise raw text. |
| `.jsonl`, `.ndjson` | JSON Lines | Each line pretty-printed when valid JSON. |
| `.yaml`, `.yml` | YAML | Requires `pyyaml`; falls back to raw text if parse fails. |
| `.docx` | DOCX | Requires `python-docx`. |
| `.xlsx` | XLSX | Requires `openpyxl`; iterates all sheets. |
| `.xls` | XLS | Requires `xlrd`. |
| `.ppt`, `.pptx` | PowerPoint | Requires `python-pptx`; extracts slide text. |
| `.pdf` | PDF | Requires `PyPDF2`; fails if no extractable text. |
| `.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`, `.tif`, `.tiff` | Image | Requires Pillow; no OCR here—image analyzer pipeline handles OCR. |
| `.xml`, `.sql`, `.dump`, `.bak`, `.env`, `.log`, `.txt` | Text | Read as UTF-8. |

## Fallback behavior

- Unknown extensions: treated as UTF-8 text.
- Missing optional dependencies: returns an error for that file type.
- Images: reader only validates; OCR + detection happen in the image pipeline.
- Archives: unreadable members are skipped; an archive with no readable members returns an error. Single-file compressions are treated as a single text source.

