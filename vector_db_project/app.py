import sys
from pathlib import Path

# Add current directory to Python path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from models.embedder import QueryEmbedder
from database.vector_store import VectorDatabase
from utils.helpers import generate_query_id
import uvicorn

app = FastAPI(title="Vector Search API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
embedder = QueryEmbedder()
db = VectorDatabase()

# Models
class QueryRequest(BaseModel):
    query: str

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

# Serve frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("frontend/index.html")

@app.post("/add")
async def add_query(request: QueryRequest):
    """Add a new query to the vector database"""
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Generate embedding
        vector = embedder.embed_query(query)
        
        # Generate ID and store
        query_id = generate_query_id(query)
        db.store_query(query_id, query, vector)
        
        return {
            "success": True,
            "id": query_id,
            "message": "Query added successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_similar(request: SearchRequest):
    """Search for similar queries"""
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Generate embedding
        vector = embedder.embed_query(query)
        
        # Search
        results = db.search_similar(vector, request.top_k)
        
        # Format results
        formatted_results = []
        for match in results.get('matches', []):
            formatted_results.append({
                "id": match['id'],
                "score": match['score'],
                "query": match['metadata'].get('query_text', 'N/A')
            })
        
        return {
            "success": True,
            "results": formatted_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        stats = db.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Vector Search API...")
    print("📍 Frontend: http://localhost:8000")
    print("📍 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
