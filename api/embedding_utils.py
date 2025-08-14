# api/embedding_utils.py
import os
import numpy as np
from dotenv import load_dotenv
load_dotenv()

HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

# If you later install and want to use the huggingface endpoint,
# you can add the real huggingface endpoint code here.
# For now we provide a deterministic fallback embedding so everything runs offline.

EMBED_DIM = 384  # arbitrary fixed dim for fallback

def _fallback_embedding(text: str):
    """
    Deterministic, simple embedding:
    - Hash token strings to seed numpy RNG so same text -> same vector
    - Return normalized float list
    """
    s = text or ""
    seed = abs(hash(s)) % (2**32)
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(EMBED_DIM)
    # normalize
    vec = vec / (np.linalg.norm(vec) + 1e-12)
    return vec.tolist()

def create_embeddings(text: str):
    """
    Returns a vector (list[float]).
    If HUGGINGFACE_API_KEY is configured and you have the HuggingFace
    endpoint package installed, add that code here. Otherwise we use the fallback.
    """
    if HUGGINGFACE_API_KEY:
        # Placeholder: If you later integrate real huggingface endpoint, implement here.
        # Example: call the HuggingFace endpoint embedding and return the vector.
        pass

    # fallback:
    return _fallback_embedding(text)
