import json
import numpy as np
from pathlib import Path

LOCAL_INDEX_FILE = Path("data/local_index.json")
_local_index = []

def load_local_index():
    """Load and prepare the local index for fast similarity search."""
    global _local_index
    
    if not LOCAL_INDEX_FILE.exists():
        print(f"Local index not found at {LOCAL_INDEX_FILE}")
        print("Run: python scripts/seed_index.py")
        return
    
    try:
        with open(LOCAL_INDEX_FILE, "r", encoding="utf-8") as f:
            _local_index = json.load(f)
        
        # Convert vectors to numpy arrays and normalize for cosine similarity
        for item in _local_index:
            vector = np.array(item["vector"], dtype=np.float32)
            # Normalize the vector
            norm = np.linalg.norm(vector)
            if norm > 0:
                item["_normalized_vector"] = vector / norm
            else:
                item["_normalized_vector"] = vector
                
        print(f"Loaded {len(_local_index)} embeddings from local index")
        
    except Exception as e:
        print(f"Error loading local index: {e}")
        _local_index = []

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two normalized vectors."""
    return float(np.dot(vec1, vec2))

def pinecone_query(user_vector, top_k=10):
    """
    Search the local index for similar professors.
    Returns list of matches with id, score, and metadata.
    """
    global _local_index
    
    # Load index if not already loaded
    if not _local_index:
        load_local_index()
    
    if not _local_index:
        return []
    
    # Normalize user vector
    user_array = np.array(user_vector, dtype=np.float32)
    user_norm = np.linalg.norm(user_array)
    if user_norm > 0:
        user_normalized = user_array / user_norm
    else:
        user_normalized = user_array
    
    # Calculate similarities
    results = []
    for item in _local_index:
        similarity = cosine_similarity(user_normalized, item["_normalized_vector"])
        results.append({
            "id": item["id"],
            "score": similarity,
            "metadata": item["metadata"]
        })
    
    # Sort by similarity score (descending)
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results[:top_k]

# Initialize on import
load_local_index()