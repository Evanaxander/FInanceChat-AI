#Adding directories to enable imports from src

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#Import document processing libraries from LangChain
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv

#Importing configuration settings from the  config module
from src.config import PDF_PATH, VECTORSTORE_PATH, USE_OPENAI, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

#Loading environment variables
load_dotenv()

def process_pdf():
    """
    Extract, chunk, and store the PDF data for the financial policy document.
    """
    print("Starting PDF processing...")
    print(f"PDF path: {PDF_PATH}")
    
    #Check if PDF exists
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF file not found at: {PDF_PATH}")
    
    # step 1 extract text and track page numbers
    print("Loading PDF...")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load() 
    print(f"Loaded {len(documents)} pages.")

    #step 2 splitting information into chunks
    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} text chunks.")
    
    #Show examples of chunks with their metadata
    print("\n--- Sample Chunks with Metadata ---")
    for i in range(min(3, len(chunks))):  # Show first 3 chunks as examples
        print(f"Chunk {i+1}:")
        print(f"  Content preview: {chunks[i].page_content[:100]}...")
        print(f"  Metadata: {chunks[i].metadata}")
        print()

    # step 3 to choose an embedding model
    if USE_OPENAI:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        embeddings = OpenAIEmbeddings()
        print("Using OpenAI embeddings...")
    else:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        print(f"Using local embeddings ({EMBEDDING_MODEL})...")
    
    #step 4 usage of FAISS to create vector database
    print("Creating vector database... This might take a few minutes.")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # step 5 database saved to drive
    os.makedirs(os.path.dirname(VECTORSTORE_PATH), exist_ok=True)
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"✅ Done! Vector index saved to '{VECTORSTORE_PATH}'")
    
    return len(chunks)

if __name__ == "__main__":
    try:
        num_chunks = process_pdf()
        print(f"\nSuccessfully processed {num_chunks} chunks from the financial policy document.")
        print("You can now run the chatbot using: python src/financial_chatbot.py")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the PDF file is in the correct location.")