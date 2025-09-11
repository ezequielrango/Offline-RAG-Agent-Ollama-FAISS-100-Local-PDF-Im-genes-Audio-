from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pathlib import Path
import shutil

# RAG core
from .rag import (
    ingest_all, build_qa, format_sources, ensure_dirs,
    DATA, PDF_DIR, IMG_DIR, AUD_DIR
)
from .db import get_conn, log_chat

# ---------- FastAPI ----------
app = FastAPI(title="Offline RAG Agent (Ollama + FAISS)", version="1.1.0")

# CORS para Vue/Go en dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IngestResponse(BaseModel):
    pdf: int
    image: int
    audio: int
    chunks: int

class QueryRequest(BaseModel):
    query: str
    k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

@app.get("/health")
def health():
    ensure_dirs()
    return {"ok": True}

@app.post("/ingest", response_model=IngestResponse)
def ingest():
    stats = ingest_all(rebuild=True)
    return stats

@app.post("/query", response_model=QueryResponse)
def query(body: QueryRequest):
    qa = build_qa(top_k=body.k)
    res = qa({"query": body.query})
    ans = res.get("result","")
    srcs = format_sources(res.get("source_documents"))
    log_chat(body.query, ans)
    return {"answer": ans, "sources": srcs}

@app.get("/documents")
def list_documents(limit: int = 50):
    with get_conn() as c:
        rows = c.execute("""SELECT id, name, path, type, pages, ocr, added_at
                            FROM documents ORDER BY id DESC LIMIT ?""",(limit,)).fetchall()
        return [dict(r) for r in rows]

@app.post("/upload")
def upload_file(kind: str = Form(...), file: UploadFile = File(...)):
    """
    kind: pdf|image|audio
    """
    ensure_dirs()
    kind = kind.lower()
    target_dir = {"pdf": PDF_DIR, "image": IMG_DIR, "audio": AUD_DIR}.get(kind)
    if not target_dir:
        return {"ok": False, "error": "kind inválido (pdf|image|audio)"}
    dest = target_dir / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"ok": True, "saved": str(dest)}

# ---------- Gradio UI (montada dentro de FastAPI en /ui) ----------
import gradio as gr

def _ui_upload(kind: str, files: List[str]):
    """Guarda archivos en las carpetas correspondientes del volumen."""
    ensure_dirs()
    if not files:
        return "No se seleccionaron archivos."
    kind = (kind or "").lower().strip()
    target_dir = {"pdf": PDF_DIR, "image": IMG_DIR, "audio": AUD_DIR}.get(kind)
    if target_dir is None:
        return "Tipo inválido. Elegí: pdf | image | audio."
    saved = []
    for f in files:
        src = Path(f)
        if not src.exists():
            continue
        dest = target_dir / src.name
        shutil.copyfile(src, dest)
        saved.append(str(dest))
    if not saved:
        return "No se pudieron guardar archivos."
    return "Guardados:\n" + "\n".join(saved)

def _ui_ingest():
    """Ejecuta la ingesta e indexado."""
    return ingest_all(rebuild=True)

def _ui_query(question: str, k: int):
    """Consulta RAG y devuelve respuesta + fuentes."""
    if not question or not question.strip():
        return "Escribí una pregunta.", []
    qa = build_qa(top_k=int(k))
    res = qa({"query": question})
    ans = res.get("result", "")
    srcs = format_sources(res.get("source_documents"))
    log_chat(question, ans)
    return ans, srcs

with gr.Blocks(title="Agente Offline RAG") as demo:
    gr.Markdown("# 🧠 Agente Offline RAG (Ollama + FAISS)")
    with gr.Tab("1) Subir archivos"):
        kind = gr.Radio(choices=["pdf", "image", "audio"], value="pdf", label="Tipo de archivo")
        files = gr.File(file_count="multiple", type="filepath", label="Arrastrá PDF/Imágenes/Audios acá")
        upload_btn = gr.Button("Subir")
        upload_out = gr.Textbox(label="Resultado de subida", lines=6)
        upload_btn.click(_ui_upload, inputs=[kind, files], outputs=[upload_out])

    with gr.Tab("2) Ingestar / Indexar"):
        gr.Markdown("Esto procesa lo subido (PDF→texto, OCR en imágenes, Whisper en audio) y construye el índice FAISS.")
        ingest_btn = gr.Button("Ingestar ahora")
        ingest_out = gr.JSON(label="Estadísticas de ingesta")
        ingest_btn.click(_ui_ingest, outputs=[ingest_out])

    with gr.Tab("3) Chat"):
        q = gr.Textbox(label="Pregunta", lines=3, placeholder="¿Qué dice el informe sobre Q4?")
        k = gr.Slider(minimum=1, maximum=10, value=5, step=1, label="Documentos Top-K")
        ask_btn = gr.Button("Consultar")
        ans = gr.Textbox(label="Respuesta", lines=8)
        src = gr.JSON(label="Fuentes (documento/página)")
        ask_btn.click(_ui_query, inputs=[q, k], outputs=[ans, src])
""" 
# Montamos la UI en /ui
app = gr.mount_gradio_app(app, demo, path="/ui")
 """