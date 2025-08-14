import os, json
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
USE_GROQ = bool(GROQ_API_KEY)

SYSTEM_PROMPT = """
You are ProfFinder, a helpful assistant that recommends university professors.

You will receive:
1) A user question.
2) A set of relevant professor snippets with provenance.

Rules:
- Use only the provided snippets as factual grounding.
- Be concise (2-4 sentences).
- Return ONLY a valid JSON object with this exact shape:

{
  "answer": "one short helpful paragraph",
  "sources": ["professor_id_1", "professor_id_2", "professor_id_3"]
}

- "sources" must reference professor_id values present in the context.
"""

def build_context_snippets(matches, max_snippets=5, max_chars=280):
    """
    Convert matches to compact snippets for the prompt.
    """
    snippets = []
    used_ids = set()
    for m in matches[:max_snippets]:
        md = m.get("metadata", {}) or {}
        pid = md.get("professor_id") or md.get("id") or m.get("id")
        if not pid:
            continue
        if pid in used_ids:
            continue
        chunk = md.get("chunk_text", "")[:max_chars]
        name = md.get("name", "")
        sub = md.get("subject", "")
        rating = md.get("avg_rating", "")
        snippets.append(f"[{pid}] {name} • {sub} • {rating}★ — {chunk}")
        used_ids.add(pid)
    return "\n".join(snippets)

def _fallback_json(matches):
    # pick top 3 professors by final_score/score
    top = []
    for m in matches:
        md = m.get("metadata", {}) or {}
        pid = md.get("professor_id") or md.get("id") or m.get("id")
        name = md.get("name", pid)
        sub = md.get("subject", "")
        rating = md.get("avg_rating", "")
        top.append((pid, name, sub, rating))
    top = top[:3]

    lines = []
    for pid, name, sub, rating in top:
        lines.append(f"{name} ({sub}, {rating}★)")
    answer = "Here are good options based on your query: " + "; ".join(lines) + "."
    sources = [pid for pid, _, _, _ in top]
    return {"answer": answer, "sources": sources}

def chat_completion_json(user_question, matches):
    """
    Returns dict: {"answer": str, "sources": [professor_id,...]}
    Tries Groq if available, otherwise returns fallback JSON.
    """
    context = build_context_snippets(matches)
    user_prompt = f"USER QUESTION:\n{user_question}\n\nCONTEXT SNIPPETS:\n{context}\n\nReturn ONLY JSON."

    if not USE_GROQ:
        return _fallback_json(matches)

    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            model="llama3-8b-8192",
            temperature=0.2,
            max_tokens=300
        )
        text = chat_completion.choices[0].message.content.strip()
        # Attempt to parse JSON strictly
        parsed = json.loads(text)
        if not isinstance(parsed, dict) or "answer" not in parsed or "sources" not in parsed:
            raise ValueError("Model did not return required JSON keys.")
        # normalize sources to list of strings
        parsed["sources"] = [str(s) for s in parsed.get("sources", [])]
        return parsed
    except Exception as e:
        # Safe fallback
        return _fallback_json(matches)
