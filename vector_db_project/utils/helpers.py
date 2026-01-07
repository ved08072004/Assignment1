import hashlib
from datetime import datetime

def generate_query_id(query: str) -> str:
    """Generate unique ID for query based on content and timestamp"""
    timestamp = datetime.now().isoformat()
    unique_string = f"{query}_{timestamp}"
    return hashlib.md5(unique_string.encode()).hexdigest()

def format_search_results(results):
    """Format search results for display"""
    if not results['matches']:
        return "No similar queries found."
    
    output = "\nSimilar queries found:\n" + "="*50 + "\n"
    for i, match in enumerate(results['matches'], 1):
        score = match['score']
        query_text = match['metadata'].get('query_text', 'N/A')
        output += f"{i}. Query: {query_text}\n"
        output += f"   Similarity: {score:.4f}\n\n"
    return output
