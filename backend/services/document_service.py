import fitz
import os
import tempfile
import logging
from infrastructure.supabase_adapter import supabase_adapter
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class DocumentService:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise e
        return text

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading TXT file: {e}")
            raise e

    @classmethod
    def fetch_and_process_file(cls, storage_path: str, ext: str) -> str:
        """Fetches a file from Supabase storage and extracts its text."""
        # Create a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            local_path = tmp.name
            
        try:
            # Download from storage
            supabase_adapter.download_file(storage_path, local_path)
            
            # Extract
            if ext.lower() == '.pdf':
                return cls.extract_text_from_pdf(local_path)
            elif ext.lower() == '.txt':
                return cls.extract_text_from_txt(local_path)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 100, overlap: int = 20) -> list[str]:
        """
        Splits text into chunks of roughly `chunk_size` words with `overlap` words.
        Since standard tokens usually map to ~0.75 words, 600 words is approx 800 tokens.
        """
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        chunks = splitter.split_text(text)

        return chunks
