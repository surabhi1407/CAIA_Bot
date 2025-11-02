import streamlit as st

st.set_page_config(page_title="CAIA Module 2 Chatbot", layout="wide")

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate

load_dotenv()
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

if not OPENAI_API_KEY:
    st.warning("Surabhi has run out of credits.Please enter Your OpenAI API Key to continue.")
    OPENAI_API_KEY = st.text_input("OpenAI API Key:", type="password")
    if not OPENAI_API_KEY:
        st.stop()

CURRENT_DIR = Path(__file__).parent
DB_DIR = Path("db/vectorstore")

@st.cache_resource
def load_vector_db():
    if not DB_DIR.exists():
        st.error("❌ Error: Vector database not found! Please preprocess your files first.")
        st.stop()
    
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    return FAISS.load_local(str(DB_DIR), embeddings, allow_dangerous_deserialization=True)

MODULE_2_INDEX = """
📖 **Module 2: Advanced AI Applications and Ethics**
- **Chapter 7**: Learning Recommender Systems
- **Chapter 8**: Principles of Computer Vision
- **Chapter 9**: Responsible and Ethical AI
- **Chapter 10**: Data Strategies in Machine Learning
"""

def create_qa_bot(vectorstore):

    #llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI_API_KEY)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 5}
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer")

    chat_template = PromptTemplate(
        input_variables=["chat_history", "question", "context"],
        template="""
        [System] You are an AI tutor specializing in CAIA(Certified Artificial Intelligence Accelerator) Module 2: Advanced AI Applications and Ethics. 
        You are NOT related to finance, investments, or portfolio management. 
        Your goal is to help users understand AI concepts, machine learning strategies, recommender systems, 
        computer vision, responsible AI, and data strategies.
        [Chat History]
        {chat_history}

        [Relevant Context from Study Material]
        {context}

        [User] {question}
        [Assistant]
        """
    )

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": chat_template}
    )

    return qa_chain

vectorstore = load_vector_db()
qa_bot = create_qa_bot(vectorstore)

#Streamlit Starts here

st.title("📖 CAIA Module 2 Chatbot")


with st.sidebar:
    st.header("🤖 Chatbot Overview")
    st.write("This chatbot helps you with **CAIA Module 2** topics including:")
    st.markdown(MODULE_2_INDEX)
    st.write("Feel free to ask about **concepts, definitions, and insights**!")

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()  

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about CAIA Module 2!"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    if any(keyword in prompt.lower() for keyword in [ "what can you do"]):
        response = f"I can help you with \n{MODULE_2_INDEX}"
    else:
        result = qa_bot({"question": prompt})  
        response = result["answer"] 

    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})