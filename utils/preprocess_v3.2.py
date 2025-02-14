
from pdf2image import convert_from_path
import os
import re
from pathlib import Path
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image, ImageEnhance
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.in_memory import InMemoryDocstore
from langchain.schema import Document
import faiss
import pickle


CURRENT_DIR = Path(__file__).parent
PDF_FILE = CURRENT_DIR.parent / "input_files" / "module4.pdf"
DB_PATH = CURRENT_DIR.parent/"db"/"module4_vectorstore" 

CHUNKS_FILE = CURRENT_DIR.parent / "db" /"chunks"/ "processed_chunks.pkl"

def debug_faiss(vectorstore):
    print(f"🛠 FAISS Index Size: {vectorstore.index.ntotal}")
    print(f"🛠 Docstore Size: {len(vectorstore.docstore._dict) if hasattr(vectorstore.docstore, '_dict') else 'Unknown'}")

    # Check first 3 stored documents
    if hasattr(vectorstore.docstore, '_dict'):
        print("🔹 Sample Stored Docs:")
        for key, value in list(vectorstore.docstore._dict.items())[:3]:
            print(f"📜 {key}: {value}")

def index_text_with_faiss(structured_chunks):

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    # Convert structured chunks to LangChain Document objects
    docs = [Document(page_content=content, metadata={"section": title}) for title, content in structured_chunks]

    # Initialize FAISS index and metadata storage
    index = faiss.IndexFlatL2(1536)  # 1536 is the OpenAI embedding size
    docstore = InMemoryDocstore({})
    index_to_docstore_id = {}

    # Create FAISS vectorstore manually
    vectorstore = FAISS(
        index=index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id,
        embedding_function=embeddings.embed_query
    )

    # Add documents to FAISS
    vectorstore.add_documents(docs)
    debug_faiss(vectorstore)
    # Save FAISS Index with metadata
    DB_PATH.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(DB_PATH))

    print(f"✅ FAISS vectorstore saved at: {DB_PATH}")

def load_chunks():
    if CHUNKS_FILE.exists():
        with open(CHUNKS_FILE, "rb") as f:
            return pickle.load(f)
    return None

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")


structured_chunks = load_chunks()

print(f"📝 Total chunks to index: {len(structured_chunks)}")
for title, content in structured_chunks[:5]:  # Print first 5 chunks
    print(f"\n🔹 {title} (First 200 chars): {content[:200]}")

index_text_with_faiss(structured_chunks)    
