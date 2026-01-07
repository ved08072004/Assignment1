import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    INDEX_NAME = os.getenv("INDEX_NAME", "project")
    MODEL_NAME = "BAAI/bge-large-en-v1.5"  # 1024 dimensions
    VECTOR_DIMENSION = 1024
