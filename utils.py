import os
import tempfile
from werkzeug.datastructures import FileStorage

try:
    import docx
except ImportError:
    docx = None

import pdfplumber

def extract_text(file: FileStorage):
    ext = os.path.splitext(file.filename)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    if ext == ".pdf":
        text = extract_text_from_pdf(tmp_path)
    elif ext == ".docx" and docx:
        text = extract_text_from_docx(tmp_path)
    elif ext == ".txt":
        text = extract_text_from_txt(tmp_path)
    else:
        text = "Unsupported file type."

    os.remove(tmp_path)
    return text

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"PDF extraction error: {e}")
    return text

def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"DOCX extraction error: {e}")
    return text

def extract_text_from_txt(file_path):
    text = ""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
    except Exception as e:
        print(f"TXT extraction error: {e}")
    return text
