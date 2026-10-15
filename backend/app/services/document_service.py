import io
import logging
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from pypdf import PdfReader
from docx import Document
from app.core.config import settings

logger = logging.getLogger("exampilote.services.document")

class DocumentService:
    """Service for extracting and validating text from study documents."""

    @staticmethod
    def extract_text(file: UploadFile, content_bytes: bytes) -> str:
        if len(content_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The uploaded file '{file.filename}' is completely empty (0 bytes on disk). Please ensure the file was completely downloaded or saved before uploading."
            )

        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(content_bytes) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed upload size of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )

        filename = file.filename or "uploaded_file.txt"
        ext = Path(filename).suffix.lower()

        if ext not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(settings.allowed_extensions_list)}"
            )

        text = ""
        try:
            if ext == ".txt":
                text = content_bytes.decode("utf-8", errors="replace")
            elif ext == ".pdf":
                reader = PdfReader(io.BytesIO(content_bytes))
                pages_text = []
                for idx, page in enumerate(reader.pages):
                    extracted = page.extract_text()
                    if extracted and extracted.strip():
                        pages_text.append(extracted.strip())
                text = "\n\n".join(pages_text)
            elif ext == ".docx":
                doc = Document(io.BytesIO(content_bytes))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                text = "\n\n".join(paragraphs)
        except Exception as e:
            logger.error(f"Document parsing error on {filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Could not parse '{filename}': {str(e)}. Please ensure the document is not corrupted or password-protected."
            )

        cleaned = text.strip()
        if not cleaned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"No readable text could be extracted from '{filename}'. "
                    "If this is a scanned image PDF, please copy and paste the text directly into the "
                    "'Study Notes / Content' box above or provide a PDF with selectable text."
                )
            )

        # Cap at 30,000 characters to prevent request timeout while providing abundant context for questions
        if len(cleaned) > 30000:
            logger.info(f"Trimming document text from {len(cleaned)} to 30000 characters for optimal AI prompt processing.")
            cleaned = cleaned[:30000]

        return cleaned
