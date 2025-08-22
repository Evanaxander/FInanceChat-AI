import os

# PDF forwarded to path
PDF_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "For Task - Policy file.pdf")

# Vector store path  
VECTORSTORE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "financial_policy_faiss_index")

# Embedding settings
USE_OPENAI = False  # Set to False to use local embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Local embedding model

#LLM settings , Set to use a local model or simple approach
USE_LOCAL_LLM = True  # Set to True to use simple local approach
CHAT_MODEL = "local"  # Placeholder for local model

# Text splitting settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200