from pathlib import Path

from pypdf import PdfReader


def load_text_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_pdf_file(path: str) -> str:
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)


def load_handbook(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix.lower()

    temp_path = Path(f"app/temp_upload{suffix}")
    temp_path.write_bytes(uploaded_file.getvalue())

    if suffix == ".txt":
        text = load_text_file(str(temp_path))
    elif suffix == ".pdf":
        text = load_pdf_file(str(temp_path))
    else:
        raise ValueError("Unsupported file type. Please upload a .txt or .pdf file.")

    temp_path.unlink(missing_ok=True)
    return text.strip()
