from builtins import set
import json

def generate_response(user_question, matches, max_professors=3):
    """
    Generate a simple, clear response based on the top matches.
    Returns a structured response with answer and sources.
    """
    if not matches:
        return {
            "answer": "No professors found matching your query.",
            "sources": []
        }
    
    # Get top professors (avoid duplicates)
    seen_professors = set()
    top_professors = []
    
    for match in matches:
        metadata = match.get('metadata', {})
        prof_id = metadata.get('professor_id')
        
        if prof_id and prof_id not in seen_professors:
            top_professors.append({
                'id': prof_id,
                'name': metadata.get('name', 'Unknown'),
                'subject': metadata.get('subject', 'Unknown Subject'),
                'rating': metadata.get('avg_rating', 0),
                'score': match.get('final_score', match.get('score', 0))
            })
            seen_professors.add(prof_id)
            
            if len(top_professors) >= max_professors:
                break
    
    if not top_professors:
        return {
            "answer": "No professors found matching your query.",
            "sources": []
        }
    
    # Generate response based on query type
    answer = generate_answer_text(user_question, top_professors)
    sources = [prof['id'] for prof in top_professors]
    
    return {
        "answer": answer,
        "sources": sources
    }

# def generate_answer_text(question, professors):
#     """Generate a natural language response."""
#     if len(professors) == 1:
#         prof = professors[0]
#         return f"I recommend {prof['name']} who teaches {prof['subject']} with a {prof['rating']}★ rating."
    
#     # Multiple professors
#     prof_list = []
#     for prof in professors:
#         prof_list.append(f"{prof['name']} ({prof['subject']}, {prof['rating']}★)")
    
#     if len(prof_list) == 2:
#         prof_str = " and ".join(prof_list)
#     else:
#         prof_str = ", ".join(prof_list[:-1]) + f", and {prof_list[-1]}"
    
#     # Determine response based on question keywords
#     question_lower = question.lower()
    
#     if any(word in question_lower for word in ['best', 'recommend', 'good']):
#         return f"Based on your query, I recommend {prof_str}."
#     elif any(word in question_lower for word in ['calculus', 'math', 'mathematics']):
#         return f"For mathematics courses, consider {prof_str}."
#     elif any(word in question_lower for word in ['chemistry', 'organic']):
#         return f"For chemistry, I suggest {prof_str}."
#     elif any(word in question_lower for word in ['computer', 'programming', 'cs']):
#         return f"For computer science, consider {prof_str}."
#     else:
#         return f"Good options for your query include {prof_str}."

def generate_answer_text(question, professors):
    q = question.lower()
    
    # Strong subject match
    if "math" in q or "calculus" in q:
        subject_filter = [p for p in professors if "math" in p["subject"].lower() or "calculus" in p["subject"].lower()]
        if subject_filter:
            professors = subject_filter
    elif "chemistry" in q or "organic" in q:
        subject_filter = [p for p in professors if "chem" in p["subject"].lower()]
        if subject_filter:
            professors = subject_filter
    elif "computer" in q or "programming" in q or "cs" in q:
        subject_filter = [p for p in professors if "computer" in p["subject"].lower() or "data" in p["subject"].lower()]
        if subject_filter:
            professors = subject_filter
    
    # Format final string
    if len(professors) == 1:
        p = professors[0]
        return f"I recommend {p['name']} who teaches {p['subject']} ({p['rating']}★)."
    else:
        prof_str = ", ".join([f"{p['name']} ({p['subject']}, {p['rating']}★)" for p in professors])
        return f"Based on your query, I recommend {prof_str}."

def chat_completion_json(user_question, matches):
    """
    Main function that returns JSON response.
    Maintains compatibility with existing code.
    """
    return generate_response(user_question, matches)