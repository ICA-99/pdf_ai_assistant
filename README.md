# 🤖 PDF AI Assistant (RAG-Based PDF Reader)

A Retrieval-Augmented Generation (RAG) application that allows users to upload a PDF and ask questions about its content using an LLM.

The application extracts text from the uploaded PDF, converts it into embeddings, stores them in a Qdrant vector database, retrieves the most relevant information for a query, and generates answers using Groq's Llama 3.1 model.

---

## 🚀 Features

- 📄 Upload a PDF document
- 💬 Ask questions about the uploaded PDF
- 🧠 Google Gemini Embeddings
- 🔍 Semantic search using Qdrant Vector Database
- 🤖 AI-generated answers with Groq (Llama 3.1)
- ⚡ FastAPI backend
- 🎨 Streamlit frontend
- 🗑 Delete uploaded PDF data from the vector database
- 📌 Supports one PDF at a time

---

## 🛠 Tech Stack

### Frontend
- Streamlit

### Backend
- FastAPI

### AI & RAG
- LangChain
- Groq (Llama 3.1)
- Google Gemini Embeddings

### Vector Database
- Qdrant

---

## 📂 Project Structure

```text
PDF_RAG/
│
├── frontend/
│   └── app.py
│
├── backend/
│   ├── main.py
│   ├── services/
│       ├── chunker.py
│       ├── embedding.py
│       ├── pdf_loader.py
│       ├── retriever.py
│       └── vector_store.py
│   
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

---

## ⚙️ How It Works

1. Upload a PDF document.
2. Extract text from the PDF.
3. Split the text into smaller chunks.
4. Generate embeddings for each chunk.
5. Store embeddings in Qdrant.
6. Convert the user's question into an embedding.
7. Retrieve the most relevant chunks.
8. Send the retrieved context to the LLM.
9. Display the generated answer.

---

## 🔄 RAG Workflow

```
PDF
 │
 ▼
Extract Text
 │
 ▼
Chunk Text
 │
 ▼
Generate Embeddings
 │
 ▼
Store in Qdrant
 │
 ▼
User Question
 │
 ▼
Query Embedding
 │
 ▼
Similarity Search
 │
 ▼
Relevant Chunks
 │
 ▼
Groq Llama 3.1
 │
 ▼
Answer
```

---

## 🚀 Installation

### Clone the repository

```bash
git clone https://github.com/your-username/PDF-RAG.git
cd PDF-RAG
```

### Create a virtual environment

```bash
python -m venv myvenv
```

### Activate it

**Windows**

```bash
myvenv\Scripts\activate
```

**Linux / macOS**

```bash
source myvenv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root.

```env
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY

GROQ_API_KEY=YOUR_GROQ_API_KEY

QDRANT_URL=YOUR_QDRANT_URL

QDRANT_API_KEY=YOUR_QDRANT_API_KEY
```

---

## ▶️ Run the Backend

```bash
uvicorn backend.main:app --reload
```

Backend runs on:

```
http://127.0.0.1:8000
```

---

## ▶️ Run the Frontend

```bash
streamlit run frontend/app.py
```

---

## 📌 Future Improvements

- Multiple PDF support
- Chat history
- PDF page highlighting
- User authentication
- Cloud deployment
- Download chat history
- Source citations
- Conversation memory

---

## 👨‍💻 Author

**Anjan Pal**

LinkedIn: https://www.linkedin.com/in/anjan-pal-ab5a5a247

---

## 📄 License

This project is intended for educational and portfolio purposes.