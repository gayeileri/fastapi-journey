from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)

async def validate_markdown_file(file: UploadFile) -> str:
    if not file.filename.endswith('.md'):
        logger.warning(f"Invalid file extension uploaded: {file.filename}")
        raise HTTPException(status_code=400, detail="Only .md files are allowed")
    
    if file.content_type not in ["text/markdown", "text/plain", "application/octet-stream"]:
        logger.warning(f"Invalid MIME type uploaded: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid MIME type")

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
