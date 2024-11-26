import os
from flask import Flask, request, jsonify
from text_processing import extract_text
from vectorstore import load_vectorstore, save_vectorstore
from openai_integration import query_openai
from langchain.schema import Document



app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the directory exists

# Initialize the vectorstore
vectorstore = None

def allowed_file(filename):
    """
    Check if a file has an allowed extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    global vectorstore
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if not file or file.filename in ("", "file"):
        return jsonify({"error": "File name is missing or invalid"}), 400

    filename = file.filename.strip()
    print(f"DEBUG: Received filename: {filename}")

    if not allowed_file(filename):
        return jsonify({"error": f"Unsupported file format: {filename}"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        # Extract text and wrap in Document
        extracted_text = extract_text(file_path)
        documents = [Document(page_content=extracted_text, metadata={"source": file_path})]

        # Save to vectorstore
        save_vectorstore(documents)
        vectorstore = load_vectorstore()
    except Exception as e:
        return jsonify({"error": f"An error occurred during file processing: {str(e)}"}), 500

    return jsonify({"message": "File uploaded and processed successfully!"}), 200


# Global variable to store chat history
chat_history = []


@app.route('/ask', methods=['POST'])
def ask_question():
    global vectorstore, chat_history

    question = request.json.get('question')
    if not question:
        return jsonify({"error": "Поставте питання."}), 400

    if vectorstore is None:
        return jsonify({"error": "Даних немає. Будь ласка, завантажте файл спочатку."}), 400

    try:
        response = query_openai(question)

        # Extract response details
        answer = response["answer"]
        sources = response["sources"]

        # Print debug information
        print(f"DEBUG: Answer: {answer}")
        for source in sources:
            print(f"DEBUG: Source: {source['text'][:100]}... (from: {source['metadata']['source']})")

        # Add the current question and answer to the chat history
        chat_history.append({"question": question, "answer": answer})

        # Return the answer and the chat history
        return jsonify({"response": answer, "history": chat_history}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    vectorstore = load_vectorstore()
    app.run(debug=True)
