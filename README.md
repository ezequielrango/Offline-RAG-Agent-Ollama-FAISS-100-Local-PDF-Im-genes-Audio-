# Offline-RAG-Agent-Ollama-FAISS-100-Local-PDF-Im-genes-Audio-
Agente multimodal (PDFs, imágenes, audios) totalmente offline. Extrae texto de PDFs con PyMuPDF, hace OCR con Tesseract, transcribe audio con Whisper, indexa con FAISS, recupera con LangChain y razona con modelos locales de Ollama (Mistral/Llama). Incluye API HTTP (FastAPI), Docker Compose y SQLite para logs/metadata.

Extrae texto de PDF con PyMuPDF (fallback OCR si están escaneados).

OCR de imágenes con Tesseract.

Transcripción de audio con Whisper (local).

Embeddings locales + FAISS para búsqueda vectorial.

RAG con LangChain + LLM local vía Ollama (Mistral/Llama).

API HTTP (FastAPI) para integrarlo con proyectos Vue o Go.

SQLite para logs/metadata (chatlog, documents, chunks).

Multimodal = soporta varias modalidades de datos (texto, imagen, audio).
Multi-model = usa varios modelos (LLM, embeddings, Whisper, Tesseract).


Stack

LLM: Ollama (mistral, llama3.1:8b-instruct, etc.)

Embeddings: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

Vector DB: FAISS

RAG: LangChain (RetrievalQA)

PDF: PyMuPDF (fallback OCR)

OCR: Tesseract + Pillow

STT (audio→texto): Whisper (local)

API: FastAPI + Uvicorn

DB: SQLite

Persistencia

./data/ → fuentes (pdfs, images, audio)

./indexes/ → índice FAISS

./storage/ → SQLite (app.db)

./hf-cache/ → caché de modelos/weights

Todos están montados como volúmenes para que no se pierdan entre reinicios.


Capturas: 
###API para comunicarse con mis proyectos locales mediante HTTP: 


<img width="346" height="148" alt="image" src="https://github.com/user-attachments/assets/48d85668-ddb7-4538-9e12-bef6073715f6" />
<img width="250" height="400" alt="image" src="https://github.com/user-attachments/assets/57c795c5-af6b-4c45-a225-d76051beeb7c" />

Screenshots (UI del proyecto): 
1)cargando contexto (audio):
Dependiendo el tipo de file se aplica extracción de texto sobre PDF, de imagenes a partir de OCR o audios a través de Whisper. Se hace chunking del texto y se generan embeddings e indexado con FAISS
<img width="1518" height="640" alt="Ingest" src="https://github.com/user-attachments/assets/8c1fbf6e-29b8-4974-8fa7-0ca8246f5e03" /> <img width="1080" height="449" alt="Embeddings+FAISS" src="https://github.com/user-attachments/assets/1b060750-8432-46bd-bb09-2dbd0bec0907" /> <img width="304" height="142" alt="FAISS saved" src="https://github.com/user-attachments/assets/ff6472cf-b8a1-4c83-adf1-47a2be007e90" />

Chatlog / Chunks / Documents
<img width="1595" height="252" alt="Chatlog" src="https://github.com/user-attachments/assets/1b3b62b5-8e47-40a0-942f-47d0f71a7864" />
<img width="1655" height="394" alt="Chunks" src="https://github.com/user-attachments/assets/3097fe9b-c192-4948-bdb5-5ea0419a43f1" />
<img width="1637" height="221" alt="Documents" src="https://github.com/user-attachments/assets/0a733c77-1a72-4a7d-813d-f866b2faca88" />
2) Prompt / Respuesta / Fuentes

k controla cuántos chunks relevantes entran al contexto. Más k = más precisión (a costa de tiempo/recursos).

<br/>
<img width="1466" height="788" alt="Prompt" src="https://github.com/user-attachments/assets/d9054820-d1b0-4744-8149-265fcb7f39df" /> <img width="1473" height="870" alt="Respuesta" src="https://github.com/user-attachments/assets/70d86be8-9754-4494-b32c-576c0fc28367" /> <img width="1417" height="887" alt="Respuesta 2" src="https://github.com/user-attachments/assets/634e8db8-adf4-45b0-90ed-05ed14d7b18f" /> <img width="1564" height="933" alt="Fuentes" src="https://github.com/user-attachments/assets/d1435ee6-e0bf-4876-9d47-d1ccb743bf0a" />
