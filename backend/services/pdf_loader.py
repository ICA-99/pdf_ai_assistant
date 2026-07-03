from langchain_community.document_loaders import PyPDFLoader


def load_pdf(file_path: str):
    # Load PDF
    loader = PyPDFLoader(file_path)

    # Convert PDF pages into Documents
    documents = loader.load()

    return documents

