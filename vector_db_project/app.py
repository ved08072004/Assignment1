import sys
from pathlib import Path

# Add current directory to Python path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from models.embedder import QueryEmbedder
from database.vector_store import VectorDatabase
from utils.helpers import generate_query_id
from utils.pdf_processor import process_pdf_file
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

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Read file content
        file_bytes = await file.read()
        
        # Validate file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(file_bytes) > max_size:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # Process PDF
        result = process_pdf_file(file_bytes, file.filename)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to process PDF'))
        
        chunks = result['chunks']
        stats = result['stats']
        
        # Generate embeddings and store chunks
        stored_count = 0
        for chunk in chunks:
            try:
                # Generate embedding for chunk
                vector = embedder.embed_query(chunk['text'])
                
                # Create unique ID for chunk
                chunk_id = f"{file.filename}_p{chunk['metadata']['page_number']}_c{chunk['metadata']['chunk_index']}"
                chunk_id = chunk_id.replace(' ', '_').replace('.pdf', '')
                
                # Store in vector database with metadata
                db.store_query(
                    query_id=chunk_id,
                    query_text=chunk['text'][:500],  # Store preview in metadata
                    vector=vector
                )
                
                # Update metadata in the index
                db.index.update(
                    id=chunk_id,
                    set_metadata={
                        'text': chunk['text'][:500],
                        'filename': chunk['metadata']['filename'],
                        'page_number': chunk['metadata']['page_number'],
                        'chunk_index': chunk['metadata']['chunk_index'],
                        'chunk_size': chunk['metadata']['chunk_size'],
                        'type': 'pdf_chunk'
                    }
                )
                
                stored_count += 1
            except Exception as e:
                print(f"Error storing chunk {chunk_id}: {str(e)}")
                continue
        
        return {
            "success": True,
            "message": f"PDF processed successfully",
            "stats": {
                **stats,
                "chunks_stored": stored_count
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print(">> Starting Vector Search API...")
    print(">> Frontend: http://localhost:8000")
    print(">> API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
