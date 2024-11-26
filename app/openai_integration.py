import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from vectorstore import load_vectorstore

# Load .env file
load_dotenv()

# Access the OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

def query_openai(question):
    """
    Query OpenAI using a language model for an answer.
    """
    vectorstore = load_vectorstore()

    if not vectorstore:
        raise Exception("Vectorstore is not initialized.")

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is missing.")

    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-4", openai_api_key=api_key),
        retriever=retriever,
        return_source_documents=True
    )

    try:
        result = qa_chain({"query": question})  # Use `__call__`
        return {
            "answer": result["result"],
            "sources": [
                {"text": doc.page_content, "metadata": doc.metadata}
                for doc in result.get("source_documents", [])
            ]
        }
    except Exception as e:
        raise RuntimeError(f"Error querying OpenAI: {str(e)}")