# Architecture & Design Decisions (DECISIONS.md)

This document outlines the architectural choices and specific implementation details for the Brief 20 Markdown Note-Taking API.

## 1. File Upload Handling & Filename Collisions
**Strategy:** We utilize FastAPI's `UploadFile` (which spools large files to disk to prevent memory overflow). 
**Validation:** The file is strictly checked for the `.md` extension, and the MIME type is validated against a whitelist (`text/markdown`, `text/plain`). Files larger than 2MB are rejected.
**Collision Prevention:** Instead of saving files to the filesystem where filename collisions could occur, the uploaded `.md` file's content is immediately extracted, decoded (UTF-8), and inserted into the PostgreSQL database as a new `Note` record. The original filename (minus the extension) is used as the default title. Because each note receives a unique auto-incrementing `id` in the database, file collisions are completely avoided.

## 2. Markdown-to-HTML Library Choice
**Library:** `markdown` (Python's official markdown library)
**Reasoning:** It is fast, standard-compliant, and extensible. Since rendering Markdown is CPU-intensive, we cache the rendered HTML using Redis. The HTML is only recomputed when the note's raw markdown content is updated (invalidating the cache on `PUT` requests).

## 3. Grammar Checking Approach
**Library:** `language-tool-python`
**Implementation:** We extract the plain text from the markdown (stripping out `#`, `**`, links, etc.) using a custom text extractor before passing it to LanguageTool. We are using `LanguageToolPublicAPI` to interact with their remote server, which removes the need to bundle Java and a heavy standalone server into our Docker container. We implemented rate-limiting on this specific endpoint using `slowapi` to protect against external API abuse and IP blocking.

## 4. Note Versioning Design
**Design:** Every time a `PUT /notes/{id}` request is made, a snapshot of the current state of the note is taken *before* the new changes are applied. This snapshot is saved to a separate `note_versions` table with a foreign key back to the parent note. 
**Details:** We increment the `version_number` by checking the highest existing version number for that note. Tags are denormalized into a comma-separated string `tags_snapshot` for historical accuracy without needing complex many-to-many historical table joins.

## 5. Smart Summarization & Auto-Tagging (OpenAI)
**Prompt Engineering:** The prompt uses a system message to instruct the model to act as a strict librarian. It demands a single, concise paragraph for the summary and exactly 5 comma-separated keywords for tags. We request JSON output to guarantee a machine-readable structure without regex parsing.
**Short Notes Handling:** If a note contains fewer than 50 words, summarization adds zero value and wastes API credits. Our `ai_tasks.py` script checks `word_count = len(markdown_content.split())`. If it is `< 50`, the task logs a skip message and gracefully exits without calling OpenAI.
**Failure Prevention (Silent Fails):** Both OpenAI calls (summary and tags) are wrapped in granular `try/except` blocks. If the summary fails, the tags generation will still run. If either fails, the error is logged via Python's built-in `logging` module so the developer can see the exact traceback in the Docker logs, preventing the task from failing silently. The background task does not affect the main thread, ensuring the API responds instantly to the user.
