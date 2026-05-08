from __future__ import annotations

from pathlib import Path

from fastapi import UploadFile

try:
    from ..errors import AppError
except ImportError:  # pragma: no cover - supports top-level test imports
    from errors import AppError


ALLOWED_EXTENSIONS = {".txt", ".pdf"}


def _validate_extension(filename: str) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise AppError("bad_request", "Unsupported file type. Use .txt or .pdf", 400)
    return extension


def _read_txt(content: bytes) -> str:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AppError("bad_request", f"Invalid UTF-8 TXT file: {exc}", 400) from exc
    return text


def _read_pdf(content: bytes) -> str:
    try:
        import fitz

        with fitz.open(stream=content, filetype="pdf") as doc:
            pages = [page.get_text("text") for page in doc]
    except Exception as exc:
        raise AppError(
            "bad_request", f"Failed to extract PDF text: {exc}", 400
        ) from exc
    return "\n".join(pages)


async def extract_text(upload: UploadFile) -> str:
    filename = upload.filename or ""
    extension = _validate_extension(filename)

    content = await upload.read()
    if not content:
        raise AppError("bad_request", "Uploaded file is empty", 400)

    text = _read_txt(content) if extension == ".txt" else _read_pdf(content)
    if not text.strip():
        raise AppError("bad_request", "No extractable text found in file", 400)
    return text
