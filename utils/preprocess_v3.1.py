
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

# Save structured chunks
def save_chunks(structured_chunks):
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(structured_chunks, f)
    print(f"✅ Stored processed chunks at: {CHUNKS_FILE}")


def index_text_with_faiss(structured_chunks):
    """
    Converts structured text chunks into FAISS embeddings for retrieval.
    """
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

    # Save FAISS Index with metadata
    DB_PATH.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(DB_PATH))

    print(f"✅ FAISS vectorstore saved at: {DB_PATH}")

# Call the function



def preprocess_image(image):
    """Convert to grayscale and enhance contrast"""
    image = image.convert("L")  # Convert to grayscale
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(2)  # Increase contrast

def pil_to_numpy(image):
    """Convert PIL image to NumPy array for PaddleOCR"""
    return np.array(image)


def split_text_smartly(ocr_text):
    """
    Splits OCR text into meaningful chunks using:
    1. Chapter & section headings
    2. Paragraph-based chunking with overlap
    """

    # Step 1: Detect chapters and section headings (case-insensitive)
    chapter_pattern = r"(chapter\s+\d+|section\s+\d+\.\d+)"
    matches = list(re.finditer(chapter_pattern, ocr_text, re.IGNORECASE))

    chunks = []
    for i in range(len(matches)):
        start_idx = matches[i].start()
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(ocr_text)
        
        section_title = matches[i].group(0)
        section_content = ocr_text[start_idx:end_idx].strip()

        # Step 2: Further split into paragraph-sized chunks (500 chars per chunk, 100 overlap)
        paragraph_chunks = []
        words = section_content.split()
        chunk_size = 80  # Adjust word count per chunk
        overlap = 20

        for j in range(0, len(words), chunk_size - overlap):
            paragraph = " ".join(words[j:j + chunk_size]).strip()
            if paragraph:
                paragraph_chunks.append((section_title, paragraph))

        chunks.extend(paragraph_chunks)

    return chunks


# def index_text_with_faiss(structured_chunks):
#     """
#     Converts structured text chunks into FAISS embeddings for retrieval.
#     """
#     embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    
#     # Convert structured chunks to LangChain Document objects
#     docs = [Document(page_content=content, metadata={"section": title}) for title, content in structured_chunks]

#     # Create FAISS vectorstore
#     vectorstore = FAISS.from_documents(docs, embeddings)

#     # Save FAISS Index
#     DB_PATH.mkdir(parents=True, exist_ok=True)
#     vectorstore.save_local(str(DB_PATH))

#     print(f"✅ FAISS vectorstore saved at: {DB_PATH}")

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")


# Convert PDF pages to images
images = convert_from_path(PDF_FILE, fmt='png', dpi=300)
images = [preprocess_image(img) for img in images]  # Preprocess images

# Convert images from PIL to NumPy (Required for PaddleOCR)
numpy_images = [pil_to_numpy(img) for img in images]

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang="en")  # Ensure English OCR model

# Run OCR on NumPy images
results = [ocr.ocr(img) for img in numpy_images]

# Convert OCR output into readable text
ocr_text = "\n".join([" ".join([word[1][0] for word in line[0]]) for line in results if line])

# Check if OCR extracted anything
if not ocr_text.strip():
    print("❌ OCR extracted empty text. Try increasing DPI or using PaddleOCR with another language model.")
    exit()

# Clean text
cleaned_ocr_text = re.sub(r'\s+', ' ', ocr_text).strip()

structured_chunks = split_text_smartly(cleaned_ocr_text)

for title, content in structured_chunks[:5]:  # Print first 5 chunks
    print(f"\n📝 {title} (First 300 chars):")
    print(content[:300])

save_chunks(structured_chunks)

# index_text_with_faiss(structured_chunks)