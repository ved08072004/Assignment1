# Vector Search Engine

A beautiful single-page web application for semantic vector search powered by AI embeddings.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn sentence-transformers pinecone python-dotenv
```

### 2. Configure Environment
Ensure your `.env` file has:
```
PINECONE_API_KEY=your_api_key
PINECONE_ENVIRONMENT=your_environment
INDEX_NAME=project
```

### 3. Run the Application
```bash
python app.py
```

### 4. Open in Browser
Navigate to: **http://localhost:8000**

## 📁 Project Structure
```
vector_db_project/
├── frontend/
│   └── index.html      # Beautiful single-page UI
├── config/
│   └── config.py       # Configuration
├── models/
│   └── embedder.py     # AI embedding model
├── database/
│   └── vector_store.py # Pinecone integration
├── utils/
│   └── helpers.py      # Helper functions
├── app.py              # FastAPI server
└── main.py             # CLI version
```

## ✨ Features

- **Add Queries**: Convert text to 1024-dimensional vectors
- **Semantic Search**: Find similar queries using AI
- **Real-time Stats**: View database statistics
- **Beautiful UI**: Modern gradient design with animations
- **REST API**: Full API documentation at `/docs`

## 🎨 Frontend Features

- Gradient purple theme
- Smooth animations
- Responsive design
- Real-time search results
- Similarity scores
- Loading states

## 🔧 API Endpoints

- `POST /add` - Add new query
- `POST /search` - Search similar queries
- `GET /stats` - Get database statistics
- `GET /docs` - API documentation

## 🧠 Model

Uses **BAAI/bge-large-en-v1.5** (1024 dimensions) for high-quality embeddings.
