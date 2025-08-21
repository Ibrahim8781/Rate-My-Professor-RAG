def rerank(matches, similarity_weight=0.6, rating_weight=0.4):
    """
    Rerank matches based on similarity score and professor rating.
    
    Args:
        matches: List of search results with score and metadata
        similarity_weight: Weight for semantic similarity (0-1)
        rating_weight: Weight for professor rating (0-1)
    
    Returns:
        Reranked list of matches
    """
    if not matches:
        return matches
    
    for match in matches:
        # Get similarity score (0-1)
        similarity_score = max(0, match.get('score', 0))
        
        # Get rating score (normalize to 0-1)
        avg_rating = match.get('metadata', {}).get('avg_rating', 0)
        rating_score = avg_rating / 5.0 if avg_rating else 0
        
        # Calculate combined score
        combined_score = (similarity_weight * similarity_score + 
                         rating_weight * rating_score)
        
        match['final_score'] = combined_score
    
    # Sort by final score (descending)
    return sorted(matches, key=lambda x: x.get('final_score', 0), reverse=True)