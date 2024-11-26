import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:5000"

st.title("Університетський помічник")

# Maintain chat history in session state
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Upload file
st.header("Завантажте файли")
uploaded_file = st.file_uploader("Завантажте файли формату PDF, Word, PowerPoint або фото!")

if uploaded_file:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    response = requests.post(f"{BACKEND_URL}/upload", files=files)
    if response.status_code == 200:
        st.success("Файл завантажено і оброблено успішно!")
    else:
        try:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
        except ValueError:
            st.error(f"Error: {response.text}")

# Ask questions
st.header("Задайте питання")
question = st.text_input("Задайте питання на основі завантаженого документа:")

if st.button("Запитати"):
    if question:
        response = requests.post(f"{BACKEND_URL}/ask", json={"question": question})
        if response.status_code == 200:
            try:
                result = response.json()

                # Update chat history in session state
                st.session_state["chat_history"] = result.get("history", [])

                # Display the latest response
                st.markdown(f"**Відповідь:** {result.get('response', 'No response')}")
            except ValueError:
                st.error(f"Error: Could not decode response. Received: {response.text}")
        else:
            st.error(f"Error: {response.status_code} - {response.text}")

# Display chat history
if st.session_state["chat_history"]:
    st.header("Історія чату")
    for idx, entry in enumerate(st.session_state["chat_history"]):
        st.markdown(f"**Q{idx + 1}:** {entry['question']}")
        st.markdown(f"**A{idx + 1}:** {entry['answer']}")
