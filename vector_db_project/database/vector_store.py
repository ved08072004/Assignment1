from pinecone import Pinecone, ServerlessSpec
from config.config import Config

class VectorDatabase:
    def __init__(self):
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        
        # Check if index exists, create if not
        if Config.INDEX_NAME not in [idx['name'] for idx in self.pc.list_indexes()]:
            print(f"Creating new index: {Config.INDEX_NAME}")
            self.pc.create_index(
                name=Config.INDEX_NAME,
                dimension=Config.VECTOR_DIMENSION,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region=Config.PINECONE_ENVIRONMENT
                )
            )
        
        self.index = self.pc.Index(Config.INDEX_NAME)
        print(f"✓ Connected to Pinecone index: {Config.INDEX_NAME}")
    
    def store_query(self, query_id: str, query_text: str, vector: list):
        """Store query vector in Pinecone"""
        self.index.upsert(
            vectors=[
                {
                    'id': query_id,
                    'values': vector,
                    'metadata': {
                        'query_text': query_text
                    }
                }
            ]
        )
        print(f"✓ Stored vector with ID: {query_id}")
    
    def search_similar(self, vector: list, top_k: int = 5):
        """Search for similar vectors"""
        results = self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )
        return results
    
    def get_stats(self):
        """Get index statistics"""
        return self.index.describe_index_stats()
