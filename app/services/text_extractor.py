from __future__ import annotations

import io
import importlib
from typing import Any, Tuple

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None
try:
    from pdf2image import convert_from_bytes
except ImportError:  # pragma: no cover
    convert_from_bytes = None
try:
    import pytesseract
except ImportError:  # pragma: no cover
    pytesseract = None
try:
    docx_module = importlib.import_module("docx")
    Document: Any = docx_module.Document
except ImportError:  # pragma: no cover
    Document = None
try:
    pptx_module = importlib.import_module("pptx")
    Presentation: Any = pptx_module.Presentation
except ImportError:  # pragma: no cover
    Presentation = None

from app.config import settings


class FileTooLargeError(Exception):
    pass


class UnsupportedFileError(Exception):
    pass


def extract_text(filename: str, content: bytes) -> Tuple[str, int]:
    lower_name = filename.lower()
    if lower_name.endswith(".pdf"):
        if pdfplumber is None:
            raise UnsupportedFileError("PDF support requires the 'pdfplumber' package")
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            page_count = len(pdf.pages)
            if page_count > settings.max_pdf_pages:
                raise FileTooLargeError("PDF exceeds maximum page limit")
            text_parts = []
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
        extracted_text = "\n".join(text_parts)
        if extracted_text.strip():
            return extracted_text, page_count

        if convert_from_bytes is None or pytesseract is None:
            raise UnsupportedFileError(
                "PDF appears to be scanned. Install 'pdf2image' and 'pytesseract' "
                "and ensure Tesseract OCR is available on the system."
            )

        images = convert_from_bytes(content, dpi=200)
        ocr_parts = [pytesseract.image_to_string(image) for image in images]
        return "\n".join(ocr_parts), page_count

    if lower_name.endswith(".docx"):
        if Document is None:
            raise UnsupportedFileError("DOCX support requires the 'python-docx' package")
        document = Document(io.BytesIO(content))
        text_parts = [para.text for para in document.paragraphs]
        return "\n".join(text_parts), len(document.paragraphs)

    if lower_name.endswith(".ppt") or lower_name.endswith(".pptx"):
        if Presentation is None:
            raise UnsupportedFileError("PowerPoint support requires the 'python-pptx' package")
        presentation = Presentation(io.BytesIO(content))
        text_parts = []
        for slide in presentation.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text_parts.append(shape.text)
        return "\n".join(text_parts), len(presentation.slides)

    raise UnsupportedFileError("Only PDF, DOCX, PPT, and PPTX files are supported")
