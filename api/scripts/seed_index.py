import json, os
from pathlib import Path
from embedding_utils import create_embeddings

DATA_FILE = Path("data/professors.json")
OUT_FILE = Path("data/local_index.json")

# simple char-based chunker (about ~150-250 tokens depending on language)
WINDOW = 600
OVERLAP = 100

def chunk_text(text, window=WINDOW, overlap=OVERLAP):
    chunks = []
    if not text:
        return chunks
    start = 0
    n = len(text)
    while start < n:
        end = min(start + window, n)
        chunk = text[start:end]
        chunks.append(chunk)
        start += window - overlap
        if start <= 0:
            break
    return chunks

def main():
    if not DATA_FILE.exists():
        raise SystemExit(f"Missing {DATA_FILE}")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        profs = json.load(f)

    index = []
    for p in profs:
        pid = p["id"]
        # Build a base text from bio + all reviews
        all_review_text = " ".join([r["text"] for r in p.get("reviews", [])])
        base_text = (p.get("bio", "") + " " + all_review_text).strip()

        # Chunk the base text
        chunks = chunk_text(base_text)

        # If nothing to chunk (short text), still create one chunk
        if not chunks:
            chunks = [base_text] if base_text else [p.get("subject", p.get("name", pid))]

        for i, chunk in enumerate(chunks):
            vector = create_embeddings(chunk)
            index.append({
                "id": f"{pid}_chunk{i}",
                "vector": vector,
                "metadata": {
                    "professor_id": pid,
                    "name": p.get("name", ""),
                    "subject": p.get("subject", ""),
                    "department": p.get("department", ""),
                    "avg_rating": p.get("avg_rating", None),
                    "num_reviews": p.get("num_reviews", None),
                    "tags": p.get("tags", []),
                    "chunk_text": chunk
                }
            })

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as out:
        json.dump(index, out)

    print(f"Seeded {OUT_FILE} with {len(index)} chunks from {len(profs)} professors")

if __name__ == "__main__":
    main()
