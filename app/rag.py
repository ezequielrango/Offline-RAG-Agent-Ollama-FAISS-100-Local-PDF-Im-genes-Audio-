from pathlib import Path
from typing import List, Dict, Optional
import os, json

import fitz                         # PyMuPDF
from PIL import Image
import pytesseract

import whisper
_WHISPER = None

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_core.documents import Document
# Splitters (LangChain 0.2+ usa paquete separado)
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # fallback para entornos con LangChain < 0.2
    from langchain.text_splitters import RecursiveCharacterTextSplitter

from langchain.chains import RetrievalQA

from .db import insert_document, insert_chunks

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
PDF_DIR = DATA / "pdfs"
IMG_DIR = DATA / "images"
AUD_DIR = DATA / "audio"
INDEX_DIR = BASE / "indexes"

DEFAULT_LLM = os.getenv("LOCAL_LLM", "deepseek-r1:7b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")


def ensure_dirs():
    for d in [PDF_DIR, IMG_DIR, AUD_DIR, INDEX_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def _whisper():
    global _WHISPER
    if _WHISPER is None:
        _WHISPER = whisper.load_model(WHISPER_MODEL)
    return _WHISPER

# ---------- PDF ----------
def extract_docs_from_pdf(pdf_path: Path) -> List[Document]:
    docs = []
    with fitz.open(pdf_path) as pdf:
        for i, page in enumerate(pdf):
            txt = page.get_text() or ""
            meta = {"source": str(pdf_path), "type": "pdf", "page": i+1, "name": pdf_path.name}
            if txt.strip():
                docs.append(Document(page_content=txt, metadata=meta))
            else:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ocr_txt = pytesseract.image_to_string(img, lang="spa+por+eng")
                meta["ocr"] = True
                docs.append(Document(page_content=ocr_txt, metadata=meta))
    return docs

# ---------- IMAGEN ----------
def ocr_image(image_path: Path) -> Document:
    txt = pytesseract.image_to_string(Image.open(image_path), lang="spa+por+eng")
    return Document(page_content=txt, metadata={
        "source": str(image_path), "type": "image", "name": image_path.name, "ocr": True
    })

# ---------- AUDIO ----------
def transcribe_audio(file_path: Path) -> Document:
    result = _whisper().transcribe(str(file_path))
    return Document(page_content=result.get("text", ""), metadata={
        "source": str(file_path), "type": "audio", "name": file_path.name, "whisper_model": WHISPER_MODEL
    })

# ---------- Split ----------
def chunk_docs(texts: List[Document], chunk_size=1000, chunk_overlap=200) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap,
        separators=["\n\n","\n"," ",""]
    )
    chunks = []
    for doc in texts:
        for c in splitter.split_text(doc.page_content):
            chunks.append(Document(page_content=c, metadata=doc.metadata))
    return chunks

# ---------- Embeddings / Index ----------
def build_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL)

def load_faiss(embeddings) -> Optional[FAISS]:
    path = INDEX_DIR / "faiss_index"
    if path.exists():
        return FAISS.load_local(str(path), embeddings=embeddings, allow_dangerous_deserialization=True)
    return None

def save_faiss(vs: FAISS):
    vs.save_local(str(INDEX_DIR / "faiss_index"))

# ---------- Ingesta ----------
def ingest_all(rebuild: bool=True) -> Dict[str,int]:
    ensure_dirs()
    all_docs: List[Document] = []

    # PDFs
    if PDF_DIR.exists():
        for p in sorted(PDF_DIR.glob("**/*.pdf")):
            ds = extract_docs_from_pdf(p)
            all_docs.extend(ds)
            doc_id = insert_document(str(p), p.name, "pdf", pages=len(ds),
                                     ocr=int(any(d.metadata.get("ocr") for d in ds)))
            _chunks = [{"text": d.page_content, "metadata_json": json.dumps(d.metadata)} for d in ds]
            insert_chunks(doc_id, _chunks)

    # Imágenes
    img_exts = {".png",".jpg",".jpeg",".tif",".tiff",".webp"}
    if IMG_DIR.exists():
        for p in sorted(IMG_DIR.glob("**/*")):
            if p.suffix.lower() in img_exts:
                d = ocr_image(p)
                all_docs.append(d)
                doc_id = insert_document(str(p), p.name, "image", ocr=1)
                insert_chunks(doc_id, [{"text": d.page_content, "metadata_json": json.dumps(d.metadata)}])

    # Audios
    aud_exts = {".wav",".mp3",".m4a",".ogg",".flac"}
    if AUD_DIR.exists():
        for p in sorted(AUD_DIR.glob("**/*")):
            if p.suffix.lower() in aud_exts:
                d = transcribe_audio(p)
                all_docs.append(d)
                doc_id = insert_document(str(p), p.name, "audio")
                insert_chunks(doc_id, [{"text": d.page_content, "metadata_json": json.dumps(d.metadata)}])

    if not all_docs:
        return {"pdf":0,"image":0,"audio":0,"chunks":0}

    chunks = chunk_docs(all_docs, 1000, 200)
    embed = build_embeddings()

    idx_dir = INDEX_DIR / "faiss_index"
    if rebuild and idx_dir.exists():
        for f in idx_dir.glob("*"): f.unlink()
        try: idx_dir.rmdir()
        except: pass

    vs = FAISS.from_documents(chunks, embed)
    save_faiss(vs)
    return {
        "pdf": sum(1 for d in all_docs if d.metadata.get("type")=="pdf"),
        "image": sum(1 for d in all_docs if d.metadata.get("type")=="image"),
        "audio": sum(1 for d in all_docs if d.metadata.get("type")=="audio"),
        "chunks": len(chunks)
    }

# ---------- QA ----------
def build_qa(top_k:int=5) -> RetrievalQA:
    embed = build_embeddings()
    vs = load_faiss(embed)
    if vs is None:
        raise RuntimeError("No existe índice. Ejecutá ingest primero.")
    retriever = vs.as_retriever(search_kwargs={"k": top_k})
    llm = Ollama(model=DEFAULT_LLM, base_url=OLLAMA_BASE_URL)
    return RetrievalQA.from_chain_type(
        llm=llm, retriever=retriever, chain_type="stuff", return_source_documents=True
    )

def format_sources(srcs: List[Document]) -> List[Dict]:
    out = []
    for d in srcs or []:
        m = d.metadata or {}
        out.append({
            "name": m.get("name"),
            "type": m.get("type"),
            "page": m.get("page"),
            "source": m.get("source")
        })
    return out

def warmup_models():
    _ = build_embeddings()
    _ = _whisper()
