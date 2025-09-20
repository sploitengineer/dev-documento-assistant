import os
from flask import Flask, request, jsonify
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from flask_cors import CORS

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# --- CONFIGURATION ---
LLM_MODEL = "phi3:mini" 
CODE_DB_PATH = "vectorstores/code"
PRACTICES_DB_PATH = "vectorstores/practices"

# --- PROMPT TEMPLATES ---
DOCUMENTATION_PROMPT = PromptTemplate(
    template="""
    Based on the following code snippet and its broader context from the codebase, please generate a comprehensive, well-formatted Python docstring.
    The docstring should start with three double-quotes (\"\"\") and end with three double-quotes (\"\"\").
    Explain the function's purpose, its arguments (if any), and what it returns.

    CONTEXT:
    {context}

    CODE:
    {code}

    DOCSTRING:
    """,
    input_variables=["context", "code"]
)

REVIEW_PROMPT = PromptTemplate(
    template="""
    As an expert code reviewer, analyze the following code snippet.
    Use the provided context from the codebase and the established best practices to provide a constructive review.
    Format your review in Markdown. Focus on clarity, potential bugs, and adherence to best practices.

    BEST PRACTICES:
    {practices}

    CODE CONTEXT:
    {context}

    CODE TO REVIEW:
    {code}

    MARKDOWN REVIEW:
    """,
    input_variables=["practices", "context", "code"]
)

# --- LOAD MODELS AND DATABASES ON STARTUP ---
try:
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    code_db = Chroma(persist_directory=CODE_DB_PATH, embedding_function=embedding_function)
    practices_db = Chroma(persist_directory=PRACTICES_DB_PATH, embedding_function=embedding_function)
    llm = Ollama(model=LLM_MODEL)
    print("Vector stores and LLM loaded successfully. Ready to assist.")
except Exception as e:
    print(f"Error loading vector stores or LLM: {e}")
    code_db = None
    practices_db = None
    llm = None

# --- API ENDPOINTS ---
@app.route('/document', methods=['POST'])
def document_code():
    data = request.json
    code = data.get('code')
    if not code or not code_db or not llm:
        return jsonify({'error': 'Invalid request or models not loaded'}), 400

    # Retrieve context from the codebase vector store
    context_docs = code_db.similarity_search(code, k=3)
    context = "\n---\n".join([doc.page_content for doc in context_docs])

    # Generate the docstring
    chain = DOCUMENTATION_PROMPT | llm
    response = chain.invoke({"context": context, "code": code})
    
    return jsonify({'documentation': response})

@app.route('/review', methods=['POST'])
def review_code():
    data = request.json
    code = data.get('code')
    if not code or not code_db or not practices_db or not llm:
        return jsonify({'error': 'Invalid request or models not loaded'}), 400
    
    # Retrieve context and best practices
    context_docs = code_db.similarity_search(code, k=2)
    practices_docs = practices_db.similarity_search(code, k=4)
    context = "\n---\n".join([doc.page_content for doc in context_docs])
    practices = "\n---\n".join([doc.page_content for doc in practices_docs])
    
    # Generate the review
    chain = REVIEW_PROMPT | llm
    response = chain.invoke({"practices": practices, "context": context, "code": code})
    
    return jsonify({'review': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

