from flask import Flask, request, jsonify
from flask_cors import CORS
from embedding_utils import create_embeddings
from pinecone_utils import pinecone_query
from reranker import rerank
from chat_completion_utils import chat_completion_json

app = Flask(__name__)
CORS(app)

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "RAG Professor Review API is running"})

@app.route('/api/search', methods=['POST'])
def search_professors():
    """
    Main search endpoint for finding professors.
    Expects JSON: {"query": "your search query"}
    """
    try:
        data = request.get_json()
        if not data or not data.get('query'):
            return jsonify({"error": "Missing 'query' parameter"}), 400
        
        user_query = data['query'].strip()
        if not user_query:
            return jsonify({"error": "Query cannot be empty"}), 400
        
        # Step 1: Create embedding for user query
        print(f"Processing query: {user_query}")
        query_vector = create_embeddings(user_query)
        
        # Step 2: Search for similar professors
        raw_matches = pinecone_query(query_vector, top_k=10)
        print(f"Found {len(raw_matches)} raw matches")
        
        # Step 3: Rerank results
        ranked_matches = rerank(raw_matches)
        top_matches = ranked_matches[:5]
        
        # Step 4: Generate response
        llm_response = chat_completion_json(user_query, top_matches)
        
        # Step 5: Format results for frontend
        formatted_matches = []
        for match in top_matches:
            metadata = match.get("metadata", {})
            formatted_matches.append({
                "id": metadata.get("professor_id", "unknown"),
                "name": metadata.get("name", "Unknown"),
                "subject": metadata.get("subject", "Unknown Subject"),
                "department": metadata.get("department", "Unknown Department"),
                "rating": metadata.get("avg_rating", 0),
                "num_reviews": metadata.get("num_reviews", 0),
                "tags": metadata.get("tags", []),
                "similarity_score": round(match.get("score", 0), 4),
                "final_score": round(match.get("final_score", 0), 4),
                "chunk_preview": metadata.get("chunk_text", "")[:200] + "..."
            })
        
        return jsonify({
            "query": user_query,
            "answer": llm_response.get("answer", ""),
            "sources": llm_response.get("sources", []),
            "professors": formatted_matches,
            "total_found": len(raw_matches)
        })
        
    except Exception as e:
        print(f"Error in search_professors: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/process', methods=['POST'])
def process():
    """Legacy endpoint for backward compatibility."""
    data = request.get_json()
    if data and 'text' in data:
        # Convert old format to new format
        data['query'] = data['text']
    return search_professors()

@app.route('/', methods=['GET'])
def home():
    """Simple home page with API information."""
    return jsonify({
        "message": "RAG Professor Review API",
        "version": "2.0",
        "endpoints": {
            "/health": "GET - Health check",
            "/api/search": "POST - Search professors (send JSON: {'query': 'your search'})",
            "/api/process": "POST - Legacy endpoint"
        },
        "example_query": {
            "url": "/api/search",
            "method": "POST",
            "body": {"query": "best math professors with clear lectures"}
        }
    })

if __name__ == '__main__':
    print("Starting RAG Professor Review API...")
    print("Visit http://localhost:5000 for API information")
    app.run(debug=True, host='0.0.0.0', port=5000)