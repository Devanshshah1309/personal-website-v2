# Indexing Blogs for RAG Chatbot

## Goal
Index blog posts so they are searchable by the RAG chatbot on the website.

## Instructions

1. Navigate to scripts directory:
   ```bash
   cd scripts
   ```

2. Update `index_blogs.py` to include your blog slug:
   ```python
   # Add at the bottom of the file, before or after existing process_blogs() calls
   process_blogs('cringe-is-a-constraint')
   ```

3. Run the indexing script:
   ```bash
   python3 index_blogs.py
   ```

## Notes
- Blog slug is the filename without `.md` extension
- Blogs starting with `DRAFT` are automatically skipped
- Script generates embeddings using Cohere API and stores them in PostgreSQL
- Requires `.env` file with `COHERE_API_KEY` and `DB_CONNECTION_STRING`
