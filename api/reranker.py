def rerank(matches, similarity_weight=0.7, rating_weight=0.25, review_count_weight=0.05):
    """
    Improved reranking that considers similarity, rating, and review count.
    
    Args:
        matches: List of search results with score and metadata
        similarity_weight: Weight for semantic similarity (0-1)
        rating_weight: Weight for professor rating (0-1) 
        review_count_weight: Weight for number of reviews (0-1)
    
    Returns:
        Reranked list of matches
    """
    if not matches:
        return matches
    
    # Find max review count for normalization
    max_reviews = max(match.get('metadata', {}).get('num_reviews', 0) for match in matches)
    max_reviews = max(max_reviews, 1)  # Avoid division by zero
    
    for match in matches:
        metadata = match.get('metadata', {})
        
        # Get similarity score (0-1, already normalized from cosine similarity)
        similarity_score = max(0, match.get('score', 0))
        
        # Get rating score (normalize to 0-1)
        avg_rating = metadata.get('avg_rating', 0)
        rating_score = avg_rating / 5.0 if avg_rating else 0
        
        # Get review count score (normalize to 0-1)
        num_reviews = metadata.get('num_reviews', 0)
        review_score = min(num_reviews / max_reviews, 1.0) if max_reviews > 0 else 0
        
        # Calculate weighted combined score
        combined_score = (
            similarity_weight * similarity_score + 
            rating_weight * rating_score +
            review_count_weight * review_score
        )
        
        match['final_score'] = combined_score
        
        # Add individual scores for debugging
        match['similarity_component'] = similarity_score
        match['rating_component'] = rating_score
        match['review_component'] = review_score
    
    # Sort by final score (descending)
    ranked = sorted(matches, key=lambda x: x.get('final_score', 0), reverse=True)
    
    # Debug info
    print(f"Reranking complete. Top result: {ranked[0]['metadata']['name']} "
          f"(final_score: {ranked[0]['final_score']:.3f})")
    
    return ranked