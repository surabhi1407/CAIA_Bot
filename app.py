import streamlit as st

st.set_page_config(page_title="CAIA Module 2 Chatbot", layout="wide")

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage



load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

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
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 5}
    )

    # Create history-aware retriever prompt
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])
    

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # Create the QA prompt template
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI tutor specializing in CAIA(Certified Artificial Intelligence Accelerator) Module 2: Advanced AI Applications and Ethics. 
        You are NOT related to finance, investments, or portfolio management. 
        Your goal is to help users understand AI concepts, machine learning strategies, recommender systems, 
        computer vision, responsible AI, and data strategies.
        
        Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise."""),
        MessagesPlaceholder("chat_history"),
        ("human", "Context: {context}\n\nQuestion: {input}")
    ])

    # Create the question answering chain
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    
    # Create the retrieval chain
    qa_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return qa_chain

vectorstore = load_vector_db()
qa_bot = create_qa_bot(vectorstore)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = InMemoryChatMessageHistory()

#Streamlit Starts here

st.title("📖 CAIA Module 2 Chatbot")


with st.sidebar:
    st.header("🤖 Chatbot Overview")
    st.write("This chatbot helps you with **CAIA Module 2** topics including:")
    st.markdown(MODULE_2_INDEX)
    st.write("Feel free to ask about **concepts, definitions, and insights**!")

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.chat_history = InMemoryChatMessageHistory()
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
        # Update chat history for special case too
        st.session_state.chat_history.add_message(HumanMessage(content=prompt))
        st.session_state.chat_history.add_message(AIMessage(content=response))
    else:
        # Invoke the chain with chat history
        result = qa_bot.invoke({
            "input": prompt,
            "chat_history": st.session_state.chat_history.messages
        })
        response = result["answer"]
        
        # Update chat history with proper message types
        st.session_state.chat_history.add_message(HumanMessage(content=prompt))
        st.session_state.chat_history.add_message(AIMessage(content=response)) 

    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})