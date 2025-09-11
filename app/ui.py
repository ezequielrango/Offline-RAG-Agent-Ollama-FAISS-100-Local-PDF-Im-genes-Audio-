# app/ui.py
from pathlib import Path
import shutil
from typing import List
import gradio as gr

from .rag import (
    ingest_all, build_qa, format_sources, ensure_dirs,
    PDF_DIR, IMG_DIR, AUD_DIR
)
from .db import log_chat

def _ui_upload(kind: str, files: List[str]):
    ensure_dirs()
    if not files:
        return "No se seleccionaron archivos."
    kind = (kind or "").lower().strip()
    target_dir = {"pdf": PDF_DIR, "image": IMG_DIR, "audio": AUD_DIR}.get(kind)
    if target_dir is None:
        return "Tipo inválido. Elegí: pdf | image | audio."
    saved = []
    for f in files:
        p = Path(f)
        if p.exists():
            dest = target_dir / p.name
            shutil.copyfile(p, dest)
            saved.append(str(dest))
    return "Guardados:\n" + "\n".join(saved) if saved else "No se pudieron guardar archivos."

def _ui_ingest():
    return ingest_all(rebuild=True)

def _ui_query(question: str, k: int):
    if not question or not question.strip():
        return "Escribí una pregunta.", []
    qa = build_qa(top_k=int(k))
    res = qa({"query": question})
    ans = res.get("result", "")
    srcs = format_sources(res.get("source_documents"))
    log_chat(question, ans)
    return ans, srcs

def build_demo():
    with gr.Blocks(title="Agente Offline RAG") as demo:
        gr.Markdown("# 🧠 Agente Offline RAG (Ollama + FAISS)")
        with gr.Tab("1) Subir archivos"):
            kind = gr.Radio(choices=["pdf", "image", "audio"], value="pdf", label="Tipo de archivo")
            files = gr.File(file_count="multiple", type="filepath", label="Arrastrá PDF/Imágenes/Audios acá")
            upload_btn = gr.Button("Subir")
            upload_out = gr.Textbox(label="Resultado de subida", lines=6)
            upload_btn.click(_ui_upload, inputs=[kind, files], outputs=[upload_out])

        with gr.Tab("2) Ingestar / Indexar"):
            gr.Markdown("Procesa lo subido (PDF→texto, OCR, Whisper) y construye FAISS.")
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
    return demo

if __name__ == "__main__":
    demo = build_demo()
    demo.queue().launch(server_name="0.0.0.0", server_port=7860, inbrowser=False, show_error=True)
