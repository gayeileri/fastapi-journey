from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)

async def validate_markdown_file(file: UploadFile) -> str:
    # Strict extension check
    filename = file.filename or ""
    if not filename.lower().endswith('.md'):
        logger.warning(f"Invalid file extension uploaded: {file.filename}")
        raise HTTPException(status_code=400, detail="Only .md files are allowed")

    # Strict MIME type whitelist for Markdown/plain text
    allowed_mimes = {"text/markdown", "text/plain", "text/x-markdown"}
    if file.content_type not in allowed_mimes:
        logger.warning(f"Invalid MIME type uploaded: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid MIME type for markdown file")

    content = await file.read()
    if len(content) > 2 * 1024 * 1024:
        logger.warning(f"File size exceeds 2MB limit: {len(content)} bytes")
        raise HTTPException(status_code=400, detail="File size exceeds 2MB")
    
    try:
        markdown_content = content.decode("utf-8")
        return markdown_content
    except UnicodeDecodeError:
        logger.error(f"Failed to decode file content as UTF-8: {file.filename}")
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")
