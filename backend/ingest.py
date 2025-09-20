import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

# Define paths for persistence
CODE_DB_PATH = "vectorstores/code"
PRACTICES_DB_PATH = "vectorstores/practices"

def ingest_code(
    project_path='.', 
    file_extensions=['.py'], 
    ignore_directories=None
):
    """
    Scans a project directory for specified file types while intelligently ignoring
    a list of folders. This function is now language-agnostic.
    """
    print(f"Starting code ingestion for file types: {file_extensions}...")

    # Use a default ignore list if none is provided
    if ignore_directories is None:
        ignore_directories = ['venv', '.git', '__pycache__', 'node_modules', '.vscode']
    
    source_files_to_ingest = []
    
    for root, dirs, files in os.walk(project_path):
        # The way to prevent os.walk from entering ignored folders
        dirs[:] = [d for d in dirs if d not in ignore_directories]
        
        for file in files:
            # Check if the file ends with any of the specified extensions
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                normalized_path = os.path.normpath(file_path)
                source_files_to_ingest.append(normalized_path)

    if not source_files_to_ingest:
        print(f"Error: No source files with extensions {file_extensions} were found.")
        return

    print(f"Found {len(source_files_to_ingest)} source files to ingest. Loading documents...")

    documents = []
    for file_path in source_files_to_ingest:
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            documents.extend(loader.load())
        except Exception as e:
            print(f"Warning: Skipping file '{file_path}' due to error: {e}")

    print(f"Successfully loaded {len(documents)} source file(s).")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # The database is created and persisted in this single step.
    Chroma.from_documents(
        texts,
        embedding_function,
        persist_directory=CODE_DB_PATH
    )
    print(f"Code ingestion complete. Vector store created at {CODE_DB_PATH}")


def ingest_practices(language='python', custom_path=None):
    """
    Ingests best practices from a specified language sub-folder or a custom path.
    """
    knowledge_base_path = custom_path
    if not knowledge_base_path:
        knowledge_base_path = os.path.join('./knowledge_base', language)

    print(f"\nStarting best practices ingestion from: {knowledge_base_path}")
    
    if not os.path.exists(knowledge_base_path):
        print(f"Error: Knowledge base directory not found at '{knowledge_base_path}'. Please create it and add your PDF/MD files.")
        return
        
    loader = DirectoryLoader(
        knowledge_base_path, 
        glob="**/*.pdf",
        loader_cls=PyMuPDFLoader,
        show_progress=True,
        use_multithreading=True
    )
    documents = loader.load()

    if not documents:
        print(f"Warning: No PDF documents found in '{knowledge_base_path}'.")
        return

    print(f"Loaded {len(documents)} document(s) from the knowledge base.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    texts = text_splitter.split_documents(documents)
    
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # The database is created and persisted in this single step.
    Chroma.from_documents(
        texts,
        embedding_function,
        persist_directory=PRACTICES_DB_PATH
    )
    print(f"Best practices ingestion complete. Vector store created at {PRACTICES_DB_PATH}")


if __name__ == "__main__":
    
    # 1. Ingest the code for a Python project
    ingest_code(file_extensions=['.py'])
    
    # 2. Ingest the best practices for the 'python' language
    ingest_practices(language='python')

