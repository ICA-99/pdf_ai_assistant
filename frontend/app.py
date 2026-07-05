import streamlit as st
import requests
import base64
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

st.set_page_config(
    page_title="PDF AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# ======================================================
# Header
# ======================================================

st.title("🤖 PDF AI Assistant")

st.markdown(
    """
Ask questions directly from your PDF using **RAG (Retrieval-Augmented Generation)**.
Upload one PDF, chat with it, and receive AI-powered answers instantly.
"""
)

st.info(
    "📌 **Only one PDF can be uploaded at a time.**\n\n"
    "Delete the current PDF before uploading another document."
)

# ======================================================
# About
# ======================================================

with st.expander("📘 About this Project"):

    st.markdown("""
### 🚀 Tech Stack

- 🎨 Streamlit (Frontend)
- ⚡ FastAPI (Backend)
- 🦜 LangChain
- 🤖 Groq (Llama 3.1)
- 🔍 Google Embeddings
- 🗂 Qdrant Vector Database

---

### 🔄 How It Works

1. 📄 Upload a PDF
2. ✂️ Extract text
3. 📚 Split into chunks
4. 🧠 Generate embeddings
5. 💾 Store embeddings in Qdrant
6. ❓ Ask a question
7. 🔍 Retrieve relevant chunks
8. 🤖 Generate an AI answer

---

### 🌟 Future Improvements

- 📄 Multiple PDF support
- 💬 Chat history
- 🖍 Highlight referenced PDF pages
- ☁️ Cloud deployment
- 🔐 User authentication
- 📥 Export chat history
- 📑 Source citations

---

### 👨‍💻 Developer

**RAG Based PDF Reader**

Created by **Anjan Pal**
""")

# ======================================================
# Session State
# ======================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

# ======================================================
# NO PDF
# ======================================================

if st.session_state.session_id is None:

    with st.container(border=True):

        st.subheader("📤 Upload PDF")

        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf"
        )

        st.write("")

        if uploaded_file is not None:

            if st.button(
                "📤 Upload PDF",
                use_container_width=True
            ):

                pdf_bytes = uploaded_file.read()

                files = {
                    "file": (
                        uploaded_file.name,
                        pdf_bytes,
                        "application/pdf"
                    )
                }

                with st.spinner("Uploading PDF..."):

                    response = requests.post(
                        f"{BASE_URL}/upload",
                        files=files
                    )

                if response.status_code == 200:

                    st.session_state.session_id = response.json()["session_id"]
                    st.session_state.pdf_bytes = pdf_bytes
                    st.session_state.pdf_name = uploaded_file.name

                    st.success("✅ PDF uploaded successfully.")

                    st.rerun()

                else:

                    st.error("Upload failed.")

# ======================================================
# PDF EXISTS
# ======================================================

else:

    st.success(f"📄 Current PDF: **{st.session_state.pdf_name}**")

    col_left, col_right = st.columns([3, 1])

    with col_right:

        if st.button(
            "🗑 Delete PDF",
            use_container_width=True
        ):

            response = requests.post(
                f"{BASE_URL}/delete",
                json={
                    "session_id": st.session_state.session_id
                }
            )

            if response.status_code == 200:

                st.session_state.session_id = None
                st.session_state.pdf_bytes = None
                st.session_state.pdf_name = None

                st.success("PDF deleted successfully.")

                st.rerun()

            else:

                st.error("Failed to delete PDF.")

    # ======================================================
    # PDF Preview
    # ======================================================

    with st.container(border=True):

        st.subheader("📖 PDF Preview")

        pdf_base64 = base64.b64encode(
            st.session_state.pdf_bytes
        ).decode()

        pdf_display = f"""
        <iframe
            src="data:application/pdf;base64,{pdf_base64}"
            width="70%"
            height="500"
            type="application/pdf">
        </iframe>
        """

        st.markdown(
            pdf_display,
            unsafe_allow_html=True
        )

    st.write("")

    # ======================================================
    # Question Section
    # ======================================================

    with st.container(border=True):

        st.subheader("💬 Ask Questions")

        question = st.text_input(
            "Enter your question about the PDF"
        )

        if st.button(
            "🔍 Ask AI",
            use_container_width=True
        ):

            if question.strip() == "":

                st.warning("Please enter a question.")

            else:

                with st.spinner("Searching relevant information..."):

                    response = requests.post(
                        f"{BASE_URL}/query",
                        json={
                            "session_id": st.session_state.session_id,
                            "query": question
                        }
                    )

                if response.status_code == 200:

                    st.markdown("### 🤖 AI Answer")

                    st.success(
                        response.json()["answer"]
                    )

                else:

                    st.error("Failed to get answer.")