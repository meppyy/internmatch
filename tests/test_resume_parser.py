from io import BytesIO
from types import SimpleNamespace

import pytest
from docx import Document
from pypdf import PdfWriter


def make_blank_pdf():
    """Create a valid PDF with no extractable text."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)

    output = BytesIO()
    writer.write(output)

    return output.getvalue()


def make_docx():
    """Create a valid DOCX with paragraphs and a table."""
    document = Document()

    document.add_paragraph("Software Developer")
    document.add_paragraph("Python and Flask experience")

    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "SQL"
    table.cell(0, 1).text = "Machine Learning"

    output = BytesIO()
    document.save(output)

    return output.getvalue()


def test_extracts_text_from_all_pdf_pages(monkeypatch):
    from app.services import resume_parser

    class FakePage:
        def __init__(self, text):
            self.text = text

        def extract_text(self):
            return self.text

    class FakePdfReader:
        def __init__(self, file_object):
            self.is_encrypted = False
            self.pages = [
                FakePage("Python and Flask development"),
                FakePage("SQL, Git and machine learning")
            ]

    monkeypatch.setattr(
        resume_parser,
        "PdfReader",
        FakePdfReader
    )

    result = resume_parser.extract_resume_text(
        b"%PDF-1.4\nfake pdf content",
        "resume.pdf"
    )

    assert "Python and Flask development" in result
    assert "SQL, Git and machine learning" in result


def test_extracts_docx_paragraphs_and_tables():
    from app.services.resume_parser import extract_resume_text

    result = extract_resume_text(
        make_docx(),
        "resume.docx"
    )

    assert "Software Developer" in result
    assert "Python and Flask experience" in result
    assert "SQL" in result
    assert "Machine Learning" in result


def test_valid_pdf_without_extractable_text_returns_empty_string():
    from app.services.resume_parser import extract_resume_text

    result = extract_resume_text(
        make_blank_pdf(),
        "scanned_resume.pdf"
    )

    assert result == ""


def test_rejects_unsupported_legacy_doc_format():
    from app.services.resume_parser import extract_resume_text

    with pytest.raises(ValueError, match="PDF and DOCX"):
        extract_resume_text(
            b"legacy document content",
            "resume.doc"
        )


def test_rejects_empty_resume_file():
    from app.services.resume_parser import extract_resume_text

    with pytest.raises(ValueError, match="empty"):
        extract_resume_text(
            b"",
            "resume.pdf"
        )


def test_rejects_invalid_pdf_signature():
    from app.services.resume_parser import extract_resume_text

    with pytest.raises(ValueError, match="valid PDF"):
        extract_resume_text(
            b"not a pdf document",
            "resume.pdf"
        )


def test_rejects_invalid_docx_package():
    from app.services.resume_parser import extract_resume_text

    with pytest.raises(ValueError, match="valid DOCX"):
        extract_resume_text(
            b"not a docx document",
            "resume.docx"
        )


def test_reports_corrupted_pdf(monkeypatch):
    from app.services import resume_parser

    class BrokenPdfReader:
        def __init__(self, file_object):
            raise RuntimeError("Invalid PDF structure")

    monkeypatch.setattr(
        resume_parser,
        "PdfReader",
        BrokenPdfReader
    )

    with pytest.raises(ValueError, match="corrupted"):
        resume_parser.extract_resume_text(
            b"%PDF-1.4\ncorrupted document",
            "resume.pdf"
        )


def test_rejects_password_protected_pdf(monkeypatch):
    from app.services import resume_parser

    class EncryptedPdfReader:
        def __init__(self, file_object):
            self.is_encrypted = True

    monkeypatch.setattr(
        resume_parser,
        "PdfReader",
        EncryptedPdfReader
    )

    with pytest.raises(ValueError, match="Password-protected"):
        resume_parser.extract_resume_text(
            b"%PDF-1.4\nencrypted document",
            "resume.pdf"
        )