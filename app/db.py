import sqlite3
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent
STORAGE = BASE / "storage"
DB_PATH = STORAGE / "app.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    STORAGE.mkdir(parents=True, exist_ok=True)
    with get_conn() as c:
        c.executescript("""
        PRAGMA journal_mode=WAL;

        CREATE TABLE IF NOT EXISTS documents (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          path TEXT UNIQUE,
          name TEXT,
          type TEXT,        -- pdf|image|audio
          pages INTEGER,
          ocr INTEGER DEFAULT 0,
          added_at TEXT
        );

        CREATE TABLE IF NOT EXISTS chunks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          document_id INTEGER,
          chunk_index INTEGER,
          text TEXT,
          metadata TEXT,
          FOREIGN KEY(document_id) REFERENCES documents(id)
        );

        CREATE TABLE IF NOT EXISTS chatlog (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          query TEXT,
          response TEXT,
          created_at TEXT
        );
        """)
        c.commit()

def insert_document(path:str, name:str, type_:str, pages:int=0, ocr:int=0) -> int:
    with get_conn() as c:
        c.execute("""INSERT OR IGNORE INTO documents(path,name,type,pages,ocr,added_at)
                     VALUES(?,?,?,?,?,?)""",
                  (path, name, type_, pages, ocr, datetime.utcnow().isoformat()))
        c.commit()
        row = c.execute("SELECT id FROM documents WHERE path=?", (path,)).fetchone()
        return int(row["id"])

def insert_chunks(doc_id:int, chunks):
    rows = [(doc_id, i, ch["text"], ch.get("metadata_json","{}")) for i, ch in enumerate(chunks)]
    with get_conn() as c:
        c.executemany("""INSERT INTO chunks(document_id,chunk_index,text,metadata)
                         VALUES(?,?,?,?)""", rows)
        c.commit()

def log_chat(query:str, response:str):
    with get_conn() as c:
        c.execute("INSERT INTO chatlog(query,response,created_at) VALUES(?,?,?)",
                  (query, response, datetime.utcnow().isoformat()))
        c.commit()
