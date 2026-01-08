from pinecone import Pinecone
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
import os
# ---------------------------
# CONFIG
# ---------------------------
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "project"
NAMESPACE = ""   # leave empty unless you used one

# ---------------------------
# CONNECT TO PINECONE
# ---------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# ---------------------------
# FETCH VECTOR IDS
# ---------------------------
stats = index.describe_index_stats()
total_vectors = stats["total_vector_count"]

print("Total vectors:", total_vectors)

# Pinecone does NOT support full scan directly
# So we do dummy vector search to fetch all IDs
dummy_vector = [0.0] * 1024

results = index.query(
    vector=dummy_vector,
    top_k=total_vectors,
    include_values=True,
    include_metadata=True,
    namespace=NAMESPACE
)

# ---------------------------
# PREPARE DATA FOR EXCEL
# ---------------------------
rows = []

for match in results["matches"]:
    # Try to get query from metadata (check common field names)
    query_text = (
        match["metadata"].get("query", "") or 
        match["metadata"].get("text", "") or 
        match["metadata"].get("query_text", "")
    )
    
    rows.append({
        "id": match["id"],
        "query_text": query_text,
        "vector": str(match["values"])   # store vector as text
    })

# Show sample of queries being exported
print(f"\n📊 Exporting {len(rows)} vectors...")
if rows:
    print("\nSample queries:")
    for i, row in enumerate(rows[:5]):  # Show first 5
        print(f"  {i+1}. {row['query_text'][:100]}...")  # First 100 chars

df = pd.DataFrame(rows)

# ---------------------------
# SAVE TO EXCEL
# ---------------------------
df.to_excel("pinecone_dump.xlsx", index=False)

print("✅ Export completed: pinecone_dump.xlsx")
