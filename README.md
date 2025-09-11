# Offline-RAG-Agent-Ollama-FAISS-100-Local-PDF-Im-genes-Audio-
Agente multimodal (PDFs, imágenes, audios) totalmente offline. Extrae texto de PDFs con PyMuPDF, hace OCR con Tesseract, transcribe audio con Whisper, indexa con FAISS, recupera con LangChain y razona con modelos locales de Ollama (Mistral/Llama). Incluye API HTTP (FastAPI), Docker Compose y SQLite para logs/metadata.
###API para comunicarse con mis proyectos locales mediante HTTP: 


<img width="346" height="148" alt="image" src="https://github.com/user-attachments/assets/48d85668-ddb7-4538-9e12-bef6073715f6" />
<img width="658" height="839" alt="image" src="https://github.com/user-attachments/assets/57c795c5-af6b-4c45-a225-d76051beeb7c" />

Screenshots: 
1)cargando contexto (audio):
Dependiendo el tipo de file se aplica extracción de texto sobre PDF. de imagenes a partir de OCR o audios a través de Whisper. Se hace chunking del texto y se almacena
<img width="1518" height="640" alt="image" src="https://github.com/user-attachments/assets/8c1fbf6e-29b8-4974-8fa7-0ca8246f5e03" />
embeddings con langchain e indexado con Faiis
<img width="1080" height="449" alt="image" src="https://github.com/user-attachments/assets/1b060750-8432-46bd-bb09-2dbd0bec0907" />
<img width="304" height="142" alt="image" src="https://github.com/user-attachments/assets/ff6472cf-b8a1-4c83-adf1-47a2be007e90" />


Chatlog: 
<img width="1595" height="252" alt="image" src="https://github.com/user-attachments/assets/1b3b62b5-8e47-40a0-942f-47d0f71a7864" />
Chunks: 
<img width="1655" height="394" alt="image" src="https://github.com/user-attachments/assets/3097fe9b-c192-4948-bdb5-5ea0419a43f1" />
Documents: 
<img width="1637" height="221" alt="image" src="https://github.com/user-attachments/assets/0a733c77-1a72-4a7d-813d-f866b2faca88" />


3) Prompt : 
<img width="1466" height="788" alt="image" src="https://github.com/user-attachments/assets/d9054820-d1b0-4744-8149-265fcb7f39df" />
Top-k como parámetro es la cantidad de chunks que debe retornar por similitud / proximidad de vectores en el contexto. Mayor cantidad de K, mayor costo computacional, tiempo y mayor precisión. Lo opuesto con menos K.
Rspuesta: 
<img width="1473" height="870" alt="image" src="https://github.com/user-attachments/assets/70d86be8-9754-4494-b32c-576c0fc28367" />
<img width="1417" height="887" alt="image" src="https://github.com/user-attachments/assets/634e8db8-adf4-45b0-90ed-05ed14d7b18f" />
Fuentes en las cuales se basó para responder, por similud, trabajando con langchain y los indices de faiss. Documento, tipo y página si aplica. 
<img width="1564" height="933" alt="image" src="https://github.com/user-attachments/assets/d1435ee6-e0bf-4876-9d47-d1ccb743bf0a" />

