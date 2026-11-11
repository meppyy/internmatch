from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader


def _combine_text(parts):
    """Combine non-empty text sections into readable text."""
    return "\n".join(
        part.strip()
        for part in parts
        if part and part.strip()
    ).strip()


def _extract_pdf_text(file_content):
    reader = PdfReader(BytesIO(file_content))

    page_text = [
        page.extract_text() or ""
        for page in reader.pages
    ]

    return _combine_text(page_text)


def _extract_docx_text(file_content):
    document = Document(BytesIO(file_content))

    text_parts = [
        paragraph.text
        for paragraph in document.paragraphs
    ]

    # Extract text from tables as well as paragraphs.
    for table in document.tables:
        for row in table.rows:
            row_text = " | ".join(
                cell.text.strip()
                for cell in row.cells
                if cell.text.strip()
            )

            if row_text:
                text_parts.append(row_text)

    return _combine_text(text_parts)


def extract_resume_text(file_content, filename):
    """
    Extract searchable text from PDF and DOCX resume files.

    Returns an empty string when a valid document contains no
    extractable text, as can happen with scanned PDFs.
    """

    if not file_content:
        raise ValueError("Resume file is empty.")

    extension = Path(filename or "").suffix.lower()

    if extension not in {".pdf", ".docx"}:
        raise ValueError(
            "Only PDF or DOCX resumes are supported."
        )

    try:
        if extension == ".pdf":
            return _extract_pdf_text(file_content)

        return _extract_docx_text(file_content)

    except Exception as error:
        raise ValueError(
            "Could not extract text from the resume."
        ) from error