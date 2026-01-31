import os
import glob
import re
import uuid
import json
import cohere
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv

# Load .env from root directory
load_dotenv(Path(__file__).parent.parent / '.env')

# --- Configuration ---
BLOG_DIR = "../src/content/blog"

COHERE_API_KEY = os.getenv("COHERE_API_KEY", default=None)
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")

def split_text_into_chunks(text, chunk_size=500):
    '''
    split text every ~chunk_size characters
    and have an overlap of ~chunk_size/5 characters
    '''
    chunks = []
    words = text.split()
    overlap_size = chunk_size // 5
    
    i = 0
    while i < len(words):
        current_chunk = ""
        # Build current chunk
        while i < len(words) and len(current_chunk) + len(words[i]) + 1 <= chunk_size:
            current_chunk += (words[i] + " ")
            i += 1
        
        chunks.append(current_chunk.strip())
        
        # Move back for overlap
        if i < len(words):
            overlap_words = []
            overlap_length = 0
            j = i - 1
            while j >= 0 and overlap_length + len(words[j]) + 1 <= overlap_size:
                overlap_words.insert(0, words[j])
                overlap_length += len(words[j]) + 1
                j -= 1
            i = j + 1  # Start next chunk from where overlap begins
    
    return chunks


# --- Helper: Get Cohere embeddings ---
def get_embeddings(text_list):
    co = cohere.Client(COHERE_API_KEY)
    response = co.embed(
        texts=text_list,
        model="embed-english-v3.0",
        input_type="search_document"
    )
    return response.embeddings

def save_records_to_file(records, filename="blog_records.json"):
    with open(filename, 'w') as f:
        json.dump(records, f)

def load_records_from_file(filename="blog_records.json"):
    with open(filename, 'r') as f:
        return json.load(f)

# --- Main processing ---
def process_blogs(blog_name=''):
    markdown_files = glob.glob(os.path.join(BLOG_DIR, "*.md"))
    records = []

    for md_path in markdown_files:
        slug = Path(md_path).stem
        if slug.startswith("DRAFT"):
            continue
        
        if blog_name and blog_name not in slug:
            continue
            
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = split_text_into_chunks(content)
        embeddings = get_embeddings(chunks)

        for chunk, embedding in zip(chunks, embeddings):
            url_path = f"/posts/{quote(slug)}"
            records.append((
                slug,                    # post_slug
                chunk,                   # content_txt
                url_path,                # url_path
                embedding,               # embedding (vector[])
            ))

        # save in case insertion fails, we don't have to regenerate embeddings
        save_records_to_file(records)

    
    records = load_records_from_file()
    insert_to_db(records)

# --- Insert into PostgreSQL ---
def insert_to_db(records):
    records = [(r[0], r[1], r[2], r[3]) for r in records]
    conn = psycopg2.connect(dsn=DB_CONNECTION_STRING)
    cursor = conn.cursor()
    sql = """
        INSERT INTO blog_chunks (post_slug, content_txt, url_path, embedding)
        VALUES %s
    """
    execute_values(cursor, sql, records)
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    if not COHERE_API_KEY:
        raise RuntimeError("COHERE_API_KEY not found in .env")
    if not DB_CONNECTION_STRING:
        raise RuntimeError("DB_CONNECTION_STRING not found in .env")
    process_blogs('cringe-is-a-constraint')