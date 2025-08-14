def rerank(matches, alpha=0.7, beta=0.3):
    """
    alpha = weight of vector similarity
    beta = weight of avg_rating
    """
    for m in matches:
        vec_score = m['score']  # from retrieval
        rating_score = m['metadata']['avg_rating'] / 5
        m['final_score'] = alpha * vec_score + beta * rating_score
    return sorted(matches, key=lambda x: x['final_score'], reverse=True)
