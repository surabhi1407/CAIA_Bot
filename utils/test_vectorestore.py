from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
import os
from pathlib import Path
from dotenv import load_dotenv
# Define the DB path
CURRENT_DIR = Path(__file__).parent
DB_PATH = CURRENT_DIR.parent / "db" / "module4_vectorstore"


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")


# Load FAISS
vectorstore = FAISS.load_local(str(DB_PATH), OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY),
allow_dangerous_deserialization=True)

# Test similarity search
query = "What is filtering?"
results = vectorstore.similarity_search(query, k=2)

# Print retrieved chunks
for i, doc in enumerate(results):
    print(f"\n🔹 Match {i+1}:")
    print(f"📜 {doc.page_content}")
    print(f"📌 Metadata: {doc.metadata}")
