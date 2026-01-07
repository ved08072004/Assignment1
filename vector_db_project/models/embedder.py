from sentence_transformers import SentenceTransformer
from config.config import Config

class QueryEmbedder:
    def __init__(self, model_name=Config.MODEL_NAME):
        self.model = SentenceTransformer(model_name)
        print(f"✓ Loaded embedding model: {model_name}")
    
    def embed_query(self, query: str) -> list:
        """Convert query text to vector embedding"""
        embedding = self.model.encode(query, convert_to_tensor=False)
        return embedding.tolist()
    
    def get_embedding_dimension(self) -> int:
        """Return the dimension of embeddings"""
        return self.model.get_sentence_embedding_dimension()
