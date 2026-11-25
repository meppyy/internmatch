from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

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
    """Extract text from a structurally valid PDF."""

    # A PDF header must appear near the beginning of the file.
    if b"%PDF-" not in file_content[:1024]:
        raise ValueError(
            "The uploaded file is not a valid PDF."
        )

    try:
        reader = PdfReader(BytesIO(file_content))

        if reader.is_encrypted:
            raise ValueError(
                "Password-protected PDFs are not supported."
            )

        if not reader.pages:
            raise ValueError(
                "The PDF does not contain any pages."
            )

        page_text = [
            page.extract_text() or ""
            for page in reader.pages
        ]

        return _combine_text(page_text)

    except ValueError:
        raise

    except Exception as error:
        raise ValueError(
            "The PDF is corrupted or cannot be read. "
            "Please upload a valid PDF."
        ) from error


def _extract_docx_text(file_content):
    """Extract text from paragraphs and tables in a valid DOCX."""

    try:
        # Validate the DOCX ZIP package before parsing it.
        with ZipFile(BytesIO(file_content)) as archive:
            contents = set(archive.namelist())

            required_files = {
                "[Content_Types].xml",
                "word/document.xml"
            }

            if not required_files.issubset(contents):
                raise ValueError(
                    "The uploaded file is not a valid DOCX document."
                )

            corrupted_file = archive.testzip()

            if corrupted_file:
                raise ValueError(
                    "The DOCX document is corrupted."
                )

        document = Document(BytesIO(file_content))

        text_parts = [
            paragraph.text
            for paragraph in document.paragraphs
        ]

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

    except ValueError:
        raise

    except Exception as error:
        raise ValueError(
            "The DOCX document is corrupted or cannot be read. "
            "Please upload a valid DOCX file."
        ) from error


def extract_resume_text(file_content, filename):
    """
    Extract searchable text from PDF and DOCX resumes.

    Returns an empty string when a valid document contains
    no extractable text, such as a scanned PDF.

    Raises ValueError for empty, unsupported or invalid files.
    """

    if not file_content:
        raise ValueError("Resume file is empty.")

    extension = Path(filename or "").suffix.lower()

    if extension not in {".pdf", ".docx"}:
        raise ValueError(
            "Only PDF and DOCX resumes are supported."
        )

    if extension == ".pdf":
        return _extract_pdf_text(file_content)

    return _extract_docx_text(file_content)