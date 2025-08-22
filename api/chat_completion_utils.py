import re

def detect_subject(query):
    """Detect subject from user query."""
    query_lower = query.lower()
    
    # Math subjects
    if any(word in query_lower for word in ['math', 'mathematics', 'calculus', 'algebra', 'geometry', 'statistics']):
        return 'math'
    
    # Computer Science
    if any(word in query_lower for word in ['computer', 'programming', 'cs', 'coding', 'software', 'data structure']):
        return 'computer'
    
    # Chemistry
    if any(word in query_lower for word in ['chemistry', 'organic', 'inorganic', 'chemical']):
        return 'chemistry'
    
    # Physics
    if any(word in query_lower for word in ['physics', 'mechanics', 'thermodynamics']):
        return 'physics'
    
    # Psychology
    if any(word in query_lower for word in ['psychology', 'psych', 'cognitive', 'behavioral']):
        return 'psychology'
    
    # Nursing/Medical
    if any(word in query_lower for word in ['nursing', 'medical', 'health', 'medicine']):
        return 'medical'
    
    # English/Writing
    if any(word in query_lower for word in ['english', 'writing', 'literature', 'creative writing']):
        return 'english'
    
    return None

def filter_by_subject(professors, target_subject):
    """Filter professors by subject relevance."""
    if not target_subject:
        return professors
    
    # Create subject mapping for better matching
    subject_keywords = {
        'math': ['math', 'calculus', 'algebra', 'statistics', 'geometry'],
        'computer': ['computer', 'data', 'programming', 'software', 'cs'],
        'chemistry': ['chemistry', 'organic', 'inorganic', 'chemical'],
        'physics': ['physics', 'mechanics', 'quantum'],
        'psychology': ['psychology', 'psych', 'cognitive', 'behavioral'],
        'medical': ['nursing', 'medical', 'health', 'medicine'],
        'english': ['english', 'writing', 'literature', 'creative writing', 'composition']
    }
    
    keywords = subject_keywords.get(target_subject, [])
    if not keywords:
        return professors
    
    # Score professors by subject relevance
    scored_profs = []
    for prof in professors:
        subject = prof.get('metadata', {}).get('subject', '').lower()
        department = prof.get('metadata', {}).get('department', '').lower()
        
        # Check if subject matches any keywords
        relevance_score = 0
        for keyword in keywords:
            if keyword in subject or keyword in department:
                relevance_score += 1
        
        if relevance_score > 0:
            prof['subject_relevance'] = relevance_score
            scored_profs.append(prof)
    
    if scored_profs:
        # Sort by subject relevance first, then by final_score
        scored_profs.sort(key=lambda x: (x.get('subject_relevance', 0), x.get('final_score', 0)), reverse=True)
        return scored_profs
    
    # If no exact matches, return top 3 original results
    return professors[:3]

def detect_query_intent(query):
    """Detect what the user is asking for."""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['list all', 'show all', 'all professors']):
        return 'list_all'
    elif any(word in query_lower for word in ['best', 'top', 'good', 'recommend']):
        return 'recommend'
    elif any(word in query_lower for word in ['worst', 'bad', 'avoid']):
        return 'avoid'
    else:
        return 'search'

def generate_smart_response(user_query, matches):
    """
    Generate a contextual response based on query intent and results.
    """
    if not matches:
        return {"answer": "No professors found matching your query. Try a different search term."}
    
    # Detect subject and filter if relevant
    target_subject = detect_subject(user_query)
    if target_subject:
        filtered_matches = filter_by_subject(matches, target_subject)
        print(f"Subject '{target_subject}' detected. Filtered from {len(matches)} to {len(filtered_matches)} professors.")
    else:
        filtered_matches = matches
    
    # Limit to top 3 for cleaner responses
    top_matches = filtered_matches[:3]
    intent = detect_query_intent(user_query)
    
    # Generate response based on intent
    if intent == 'list_all':
        answer = generate_list_response(top_matches)
    elif intent == 'recommend':
        answer = generate_recommendation_response(user_query, top_matches, target_subject)
    else:
        answer = generate_search_response(user_query, top_matches, target_subject)
    
    return {
        "answer": answer,
        "filtered_professors": top_matches  # Return filtered results for consistency
    }

def generate_recommendation_response(query, professors, subject):
    """Generate recommendation-style response."""
    if len(professors) == 1:
        prof = professors[0]['metadata']
        rating = prof.get('avg_rating', 0)
        return f"I recommend {prof['name']} who teaches {prof['subject']} with a {rating}⭐ rating."
    
    # Multiple professors
    if subject:
        subject_name = {
            'math': 'mathematics',
            'computer': 'computer science', 
            'chemistry': 'chemistry',
            'physics': 'physics',
            'psychology': 'psychology',
            'medical': 'medical/nursing',
            'english': 'English/writing'
        }.get(subject, 'your subject')
        
        prof_list = []
        for prof in professors:
            metadata = prof['metadata']
            rating = metadata.get('avg_rating', 0)
            prof_list.append(f"{metadata['name']} ({rating}⭐)")
        
        return f"For {subject_name}, I recommend: {', '.join(prof_list)}."
    
    else:
        # General recommendation
        prof_list = []
        for prof in professors:
            metadata = prof['metadata']
            rating = metadata.get('avg_rating', 0)
            subject = metadata.get('subject', 'Unknown')
            prof_list.append(f"{metadata['name']} ({subject}, {rating}⭐)")
        
        return f"Based on your query, I recommend: {', '.join(prof_list)}."

def generate_search_response(query, professors, subject):
    """Generate search-style response."""
    if len(professors) == 1:
        prof = professors[0]['metadata']
        rating = prof.get('avg_rating', 0)
        return f"Found: {prof['name']} - {prof['subject']} ({rating}⭐)"
    
    prof_count = len(professors)
    top_prof = professors[0]['metadata']
    rating = top_prof.get('avg_rating', 0)
    
    return f"Found {prof_count} professors. Top match: {top_prof['name']} - {top_prof['subject']} ({rating}⭐)"

def generate_list_response(professors):
    """Generate list-style response."""
    prof_list = []
    for i, prof in enumerate(professors, 1):
        metadata = prof['metadata']
        rating = metadata.get('avg_rating', 0)
        prof_list.append(f"{i}. {metadata['name']} - {metadata['subject']} ({rating}⭐)")
    
    return "Here are the professors:\n" + "\n".join(prof_list)

# Legacy function for backward compatibility
def chat_completion_json(user_question, matches):
    """Legacy function - redirects to new system."""
    return generate_smart_response(user_question, matches)