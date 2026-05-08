from __future__ import annotations

import asyncio
import io

from fastapi import UploadFile

from errors import AppError
from services.file_extraction_service import extract_text


def test_extract_text_from_txt() -> None:
    upload = UploadFile(
        filename="sample.txt", file=io.BytesIO("hello world".encode("utf-8"))
    )
    text = asyncio.run(extract_text(upload))
    assert text == "hello world"


def test_reject_invalid_extension() -> None:
    upload = UploadFile(filename="sample.docx", file=io.BytesIO(b"abc"))
    try:
        asyncio.run(extract_text(upload))
    except AppError:
        return
    raise AssertionError("Expected AppError for invalid extension")
