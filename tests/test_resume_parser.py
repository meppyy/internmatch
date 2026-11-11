from types import SimpleNamespace

import pytest


def test_extracts_text_from_all_pdf_pages(monkeypatch):
    from app.services import resume_parser

    class FakePage:
        def __init__(self, text):
            self.text = text

        def extract_text(self):
            return self.text

    class FakePdfReader:
        def __init__(self, file_object):
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
        b"fake pdf content",
        "resume.pdf"
    )

    assert "Python and Flask development" in result
    assert "SQL, Git and machine learning" in result


def test_extracts_docx_paragraphs_and_tables(monkeypatch):
    from app.services import resume_parser

    fake_document = SimpleNamespace(
        paragraphs=[
            SimpleNamespace(text="Software Developer"),
            SimpleNamespace(text="Python and Flask experience")
        ],
        tables=[
            SimpleNamespace(
                rows=[
                    SimpleNamespace(
                        cells=[
                            SimpleNamespace(text="SQL"),
                            SimpleNamespace(text="Machine Learning")
                        ]
                    )
                ]
            )
        ]
    )

    monkeypatch.setattr(
        resume_parser,
        "Document",
        lambda file_object: fake_document
    )

    result = resume_parser.extract_resume_text(
        b"fake docx content",
        "resume.docx"
    )

    assert "Software Developer" in result
    assert "Python and Flask experience" in result
    assert "SQL" in result
    assert "Machine Learning" in result


def test_rejects_unsupported_legacy_doc_format():
    from app.services.resume_parser import extract_resume_text

    with pytest.raises(ValueError, match="PDF or DOCX"):
        extract_resume_text(
            b"legacy document content",
            "resume.doc"
        )


def test_rejects_empty_resume_file():
    from app.services.resume_parser import extract_resume_text

    with pytest.raises(ValueError, match="empty"):
        extract_resume_text(b"", "resume.pdf")


def test_reports_unreadable_pdf(monkeypatch):
    from app.services import resume_parser

    class BrokenPdfReader:
        def __init__(self, file_object):
            raise RuntimeError("Invalid PDF structure")

    monkeypatch.setattr(
        resume_parser,
        "PdfReader",
        BrokenPdfReader
    )

    with pytest.raises(ValueError, match="Could not extract text"):
        resume_parser.extract_resume_text(
            b"invalid pdf",
            "resume.pdf"
        )