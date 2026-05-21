import logging
from app.core.database import SessionLocal
from app.models.note import Note
from app.services.openai_service import generate_summary, generate_tags

logger = logging.getLogger(__name__)

def process_note_background(note_id: int):
    db = SessionLocal()
    try:
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            logger.warning(f"Note {note_id} not found for background processing.")
            return

        word_count = len(note.markdown_content.split())
        if word_count < 50:
            logger.info(f"Skipping summary for note {note_id}: word count {word_count} < 50.")
            return

        try:
            summary = generate_summary(note.markdown_content)
            if summary:
                note.summary = summary
        except Exception as e:
            logger.error(f"Failed to generate summary for note {note_id}: {e}")

        try:
            tags = generate_tags(note.markdown_content)
            if tags:
                note.suggested_tags = tags
        except Exception as e:
            logger.error(f"Failed to generate tags for note {note_id}: {e}")

        db.commit()
        logger.info(f"Successfully processed AI tasks for note {note_id}.")

    except Exception as e:
        logger.exception(f"Unexpected error in background task for note {note_id}: {str(e)}")
    finally:
        db.close()
