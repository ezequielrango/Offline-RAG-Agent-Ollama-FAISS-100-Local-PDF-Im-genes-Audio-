# Offline RAG Agent — 100% Local (PDF · Imágenes · Audio)

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Docker](https://img.shields.io/badge/Docker-Compose-informational)
![LangChain](https://img.shields.io/badge/LangChain-RAG-orange)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20DB-yellow)
![Whisper](https://img.shields.io/badge/Whisper-STT-purple)
![Tesseract](https://img.shields.io/badge/Tesseract-OCR-lightgrey)
![Ollama](https://img.shields.io/badge/Ollama-LLMs-black)

Agente **multimodal** (PDFs, imágenes y audios) 100% **offline**.  
Extrae texto de **PDF** con PyMuPDF (con *fallback* de **OCR** si están escaneados), **OCR** de imágenes con Tesseract, **transcribe audio** con Whisper, genera **embeddings** locales, **indexa con FAISS**, recupera con **LangChain** y **razona con LLMs locales** vía **Ollama** (Mistral/Llama).  
Incluye **API HTTP** (FastAPI), **Docker Compose** y **SQLite** para logs/metadata.

> **Multimodal** = varias **modalidades** de datos (texto, imagen, audio).  
> **Multi-model** = varios **modelos** en la arquitectura (LLM, embeddings, Whisper, Tesseract).

---

## Como ejecutar

git clone y docker compose up -d


---

## Características

* 100% **local** (sin nube).
* **PDF** → texto con PyMuPDF (+ OCR si hace falta).
* **Imágenes** → texto con **Tesseract**.
* **Audio** → texto con **Whisper** (local).
* **Embeddings** locales + **FAISS** para búsqueda vectorial.
* **RAG** con **LangChain** + **LLM** vía **Ollama**.
* **API HTTP** para integrarlo con **Vue** o **Go**.
* **SQLite** para `chatlog`, `documents` y `chunks`.

---

## Stack

| Componente | Elección |
|-----------:|:---------|
| **LLM** | Ollama (`mistral`, `llama3.1:8b-instruct`, etc.) |
| **Embeddings** | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| **Vector DB** | FAISS |
| **RAG** | LangChain (RetrievalQA) |
| **PDF** | PyMuPDF (*fallback* OCR) |
| **OCR** | Tesseract + Pillow |
| **STT (audio → texto)** | Whisper (local) |
| **API** | FastAPI + Uvicorn |
| **DB** | SQLite |

---

## Arquitectura


Flujo:
1. Ingesta recorre `data/` y extrae texto de PDFs (PyMuPDF + OCR), imágenes (OCR), y audios (Whisper).  
2. Hace *chunking*, genera **embeddings** y construye/actualiza el índice **FAISS**.  
3. En `/query`, LangChain recupera los **k** chunks más relevantes y los pasa al **LLM** (Ollama) para responder.  
4. Se loguean consultas y respuestas en **SQLite**.


Persistencia

./data/ → fuentes (pdfs, images, audio)

./indexes/ → índice FAISS

./storage/ → SQLite (app.db)

./hf-cache/ → caché de modelos/weights

Todos están montados como volúmenes para que no se pierdan entre reinicios.

--- 

# Capturas: 
## API para comunicarse con mis proyectos locales mediante HTTP: 


<img width="346" height="148" alt="image" src="https://github.com/user-attachments/assets/48d85668-ddb7-4538-9e12-bef6073715f6" />
<img width="250" height="400" alt="image" src="https://github.com/user-attachments/assets/57c795c5-af6b-4c45-a225-d76051beeb7c" />
---

## Screenshots (UI del proyecto): 
## 1)cargando contexto (audio):
Dependiendo el tipo de file se aplica extracción de texto sobre PDF, de imagenes a partir de OCR o audios a través de Whisper. Se hace chunking del texto y se generan embeddings e indexado con FAISS <br/>
<img width="1518" height="640" alt="Ingest" src="https://github.com/user-attachments/assets/8c1fbf6e-29b8-4974-8fa7-0ca8246f5e03" /> <img width="1080" height="449" alt="Embeddings+FAISS" src="https://github.com/user-attachments/assets/1b060750-8432-46bd-bb09-2dbd0bec0907" /> <img width="304" height="142" alt="FAISS saved" src="https://github.com/user-attachments/assets/ff6472cf-b8a1-4c83-adf1-47a2be007e90" />

## Chatlog / Chunks / Documents
<img width="1595" height="252" alt="Chatlog" src="https://github.com/user-attachments/assets/1b3b62b5-8e47-40a0-942f-47d0f71a7864" />
<img width="1655" height="394" alt="Chunks" src="https://github.com/user-attachments/assets/3097fe9b-c192-4948-bdb5-5ea0419a43f1" />
<img width="1637" height="221" alt="Documents" src="https://github.com/user-attachments/assets/0a733c77-1a72-4a7d-813d-f866b2faca88" /> <br/>
## 2) Prompt / Respuesta / Fuentes

k (top-k) controla cuántos chunks relevantes recupera el retriever por similitud vectorial.
Más k → más contexto y, en general, mejor precisión (mayor tiempo/CPU/RAM).
Menos k → respuestas más rápidas (riesgo de perder contexto clave).
<br/>
<img width="1466" height="788" alt="Prompt" src="https://github.com/user-attachments/assets/d9054820-d1b0-4744-8149-265fcb7f39df" /> <img width="1473" height="870" alt="Respuesta" src="https://github.com/user-attachments/assets/70d86be8-9754-4494-b32c-576c0fc28367" /> <img width="1417" height="887" alt="Respuesta 2" src="https://github.com/user-attachments/assets/634e8db8-adf4-45b0-90ed-05ed14d7b18f" /> <img width="1564" height="933" alt="Fuentes" src="https://github.com/user-attachments/assets/d1435ee6-e0bf-4876-9d47-d1ccb743bf0a" />

# Endpoints HTTP
Base URL: http://localhost:8000

| Método |   Endpoint   | Descripción                                                                     |       |                           |
| :----: | :----------: | :------------------------------------------------------------------------------ | ----- | ------------------------- |
|  `GET` |   `/health`  | Ping/ready check → `{ "ok": true }`                                             |       |                           |
| `POST` |   `/ingest`  | Recorre `data/`, extrae texto (PDF/Imagen/Audio), *chunking* y (re)indexa FAISS |       |                           |
| `POST` |   `/query`   | Pregunta RAG: body `{ "query": "texto", "k": 5 }`                               |       |                           |
|  `GET` | `/documents` | Lista documentos (últimos N)                                                    |       |                           |
| `POST` |   `/upload`  | Subida multipart (\`kind=pdf                                                    | image | audio`, `file=@archivo\`) |


# Ejemplos rápidos: 
```
# Ingestar
curl -X POST http://localhost:8000/ingest

# Preguntar
curl -s -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"¿Qué capítulos hablan de seguridad?","k":4}' | jq

# Subir un PDF
curl -F kind=pdf -F file=@./mis_docs/informe.pdf http://localhost:8000/upload

```
## Ejemplos (cURL / Vue / Go)

### Vue / TypeScript

```
export async function askLocalRAG(query: string, k = 5) {
  const res = await fetch("http://localhost:8000/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, k }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json(); // { answer, sources[] }
}


```

### Go

```
type QueryReq struct {
  Query string `json:"query"`
  K     int    `json:"k"`
}
type QueryRes struct {
  Answer  string                   `json:"answer"`
  Sources []map[string]interface{} `json:"sources"`
}


```
