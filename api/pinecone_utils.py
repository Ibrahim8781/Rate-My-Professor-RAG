import os, json
from pathlib import Path
import numpy as np

# Optional Pinecone imports guarded
USE_PINECONE = os.environ.get("USE_PINECONE", "0") == "1"
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX", "professor")
PINECONE_NAMESPACE = os.environ.get("PINECONE_NAMESPACE", "ns1")

LOCAL_INDEX_FILE = Path("data/local_index.json")

pc = None
index = None

if USE_PINECONE:
    try:
        from pinecone import Pinecone
        api_key = os.environ.get("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError("PINECONE_API_KEY not set")
        pc = Pinecone(api_key=api_key)
        index = pc.Index(PINECONE_INDEX_NAME)
    except Exception as e:
        print(f"[pinecone_utils] Pinecone init failed, falling back to local. Reason: {e}")
        USE_PINECONE = False

# Load local index once
_local_index = []
if LOCAL_INDEX_FILE.exists():
    try:
        with open(LOCAL_INDEX_FILE, "r", encoding="utf-8") as f:
            _local_index = json.load(f)
        # normalize vectors to numpy arrays for fast cosine
        for item in _local_index:
            v = np.array(item["vector"], dtype=np.float32)
            norm = np.linalg.norm(v) + 1e-12
            item["_v"] = v / norm
    except Exception as e:
        print(f"[pinecone_utils] Failed to load local index: {e}")
else:
    print(f"[pinecone_utils] Local index not found at {LOCAL_INDEX_FILE}. Run scripts/seed_index.py")

def _cosine(a, b):
    # a is np.array (normalized), b is np.array (normalize first)
    bn = b / (np.linalg.norm(b) + 1e-12)
    return float(np.dot(a, bn))

def _local_query(user_vector, top_k=5):
    if not _local_index:
        return []
    user_v = np.array(user_vector, dtype=np.float32)
    user_v = user_v / (np.linalg.norm(user_v) + 1e-12)

    scored = []
    for item in _local_index:
        score = float(np.dot(item["_v"], user_v))
        scored.append({
            "id": item["id"],
            "score": score,
            "metadata": item["metadata"]
        })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

def pinecone_query(user_vector, top_k=5):
    """
    Returns a list of dicts: [{id, score, metadata}, ...]
    Uses Pinecone if enabled; otherwise queries local index.
    """
    if USE_PINECONE and index is not None:
        try:
            res = index.query(
                namespace=PINECONE_NAMESPACE,
                vector=user_vector,
                top_k=top_k,
                include_metadata=True
            )
            out = []
            for m in res.matches:
                out.append({
                    "id": m.id,
                    "score": m.score,
                    "metadata": m.metadata
                })
            return out
        except Exception as e:
            print(f"[pinecone_utils] Pinecone query failed, falling back to local. Reason: {e}")

    # fallback local
    return _local_query(user_vector, top_k=top_k)
