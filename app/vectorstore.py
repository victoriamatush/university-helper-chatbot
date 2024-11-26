from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access the OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

# Global variable for storing the vector store
vectorstore = None

def save_vectorstore(documents):
    """
    Save documents' embeddings in FAISS vector store.
    """
    global vectorstore

    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    vectorstore = FAISS.from_documents(documents, embeddings)

def load_vectorstore():
    """
    Load vector store to retrieve relevant documents.
    """
    global vectorstore
    return vectorstore
