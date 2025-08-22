from flask import Flask, request, jsonify
from flask_cors import CORS
from embedding_utils import create_embeddings
from pinecone_utils import pinecone_query
from reranker import rerank
from chat_completion_utils import generate_smart_response

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
        
        print(f"Processing query: {user_query}")
        
        # Step 1: Create embedding for user query
        query_vector = create_embeddings(user_query)
        
        # Step 2: Search for similar professors (get more to allow for filtering)
        raw_matches = pinecone_query(query_vector, top_k=20)
        print(f"Found {len(raw_matches)} raw matches")
        
        # Step 3: Remove duplicates by professor_id (keep highest score)
        seen_professors = {}
        for match in raw_matches:
            prof_id = match.get("metadata", {}).get("professor_id")
            if prof_id:
                if prof_id not in seen_professors or match.get("score", 0) > seen_professors[prof_id].get("score", 0):
                    seen_professors[prof_id] = match
        
        unique_matches = list(seen_professors.values())
        print(f"After deduplication: {len(unique_matches)} unique professors")
        
        # Step 4: Rerank results
        ranked_matches = rerank(unique_matches)
        top_matches = ranked_matches[:5]
        
        # Step 5: Generate smart response (this will also filter by subject)
        response_data = generate_smart_response(user_query, top_matches)
        
        # Use the same filtered results for the professor list
        final_professors = response_data.get("filtered_professors", top_matches)
        
        # Step 6: Format results for frontend
        formatted_matches = []
        for match in final_professors:
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
                "bio": metadata.get("bio", "")
            })
        
        return jsonify({
            "query": user_query,
            "answer": response_data["answer"],
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
    
    # Call search and adapt response format for frontend
    response = search_professors()
    if response.status_code == 200:
        search_data = response.get_json()
        # Adapt to frontend expectations
        return jsonify({
            "llm_answer": search_data.get("answer"),
            "matches": search_data.get("professors", [])
        })
    return response

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