from sentence_transformers import SentenceTransformer
import os

# Load the model once globally for efficiency
model = None

def get_model():
    global model
    if model is None:
        print("Loading embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded successfully!")
    return model

def create_embeddings(text: str):
    """
    Create embeddings using sentence-transformers.
    Returns a list of floats representing the text embedding.
    """
    if not text or not text.strip():
        text = "empty"
    
    try:
        model = get_model()
        # Get embedding and convert to list
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    except Exception as e:
        print(f"Error creating embedding: {e}")
        # Fallback: return zero vector of standard size
        return [0.0] * 384