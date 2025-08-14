from flask import Flask, request, jsonify
from flask_cors import CORS
from embedding_utils import create_embeddings
from pinecone_utils import pinecone_query
from reranker import rerank
from chat_completion_utils import chat_completion_json

app = Flask(__name__)
CORS(app)  # open for local dev; tighten in prod

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/process', methods=['POST'])
def process():
    data = request.json or {}
    user_text = data.get('text')
    if not user_text or not user_text.strip():
        return jsonify({"error": "Invalid input"}), 400

    # 1) Embed the question
    qvec = create_embeddings(user_text)

    # 2) Retrieve (local or Pinecone)
    raw_matches = pinecone_query(qvec, top_k=10)  # get more, then rerank

    # 3) Rerank with rating-aware score
    ranked = rerank(raw_matches, alpha=0.7, beta=0.3)
    top5 = ranked[:5]

    # 4) Ask the LLM (or fallback) for JSON answer with sources
    llm_json = chat_completion_json(user_text, top5)

    # 5) Format return: llm answer, cited sources list, and full matches for UI
    # normalize matches for frontend
    ui_matches = []
    for m in top5:
        md = m.get("metadata", {}) or {}
        ui_matches.append({
            "id": md.get("professor_id") or m.get("id"),
            "name": md.get("name"),
            "subject": md.get("subject"),
            "department": md.get("department"),
            "stars": md.get("avg_rating"),
            "review": md.get("chunk_text", ""),   # chunk snippet
            "score": round(float(m.get("final_score", m.get("score", 0.0))), 4)
        })

    return jsonify({
        "llm_answer": llm_json.get("answer"),
        "sources_used": llm_json.get("sources", []),
        "matches": ui_matches
    })

if __name__ == '__main__':
    app.run(debug=True)
