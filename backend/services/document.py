import fitz  # PyMuPDF
import os

class DocumentService:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extracts text from a PDF file using PyMuPDF."""
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            raise e
        return text

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extracts text from a TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading TXT file: {e}")
            raise e

    @classmethod
    def process_file(cls, file_path: str) -> str:
        """Processes a file based on its extension."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return cls.extract_text_from_pdf(file_path)
        elif ext == '.txt':
            return cls.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
