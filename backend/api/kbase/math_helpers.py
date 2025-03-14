import math
from typing import List

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

def mmr(
    query: List[float],
    candidate_vectors: List[List[float]],
    candidate_chunks: List,
    k: int,
    lambda_: float = 0.5
) -> List:
    """
    Maximal Marginal Relevance (MMR) selection.
    
    Args:
        query: The query embedding.
        candidate_vectors: List of candidate embedding vectors.
        candidate_chunks: List of candidate chunks (or documents) corresponding to the candidate_vectors.
        k: Number of results to select.
        lambda_: Trade-off parameter between relevance and diversity.
    
    Returns:
        A list of k candidate chunks selected using MMR.
    """
    if not candidate_vectors:
        return []
    
    # Compute cosine similarities between query and each candidate.
    sims_to_query = [cosine_similarity(query, vec) for vec in candidate_vectors]
    # Initialize the selected set with the most relevant candidate.
    selected = [max(range(len(sims_to_query)), key=lambda i: sims_to_query[i])]
    remaining = set(range(len(candidate_vectors))) - set(selected)
    
    while len(selected) < k and remaining:
        mmr_scores = {}
        for i in remaining:
            sim_to_query = cosine_similarity(query, candidate_vectors[i])
            # For diversity, find the maximum similarity to any already selected candidate.
            max_sim_to_selected = max(cosine_similarity(candidate_vectors[i], candidate_vectors[j]) for j in selected)
            mmr_score = lambda_ * sim_to_query - (1 - lambda_) * max_sim_to_selected
            mmr_scores[i] = mmr_score
        best_i = max(mmr_scores, key=mmr_scores.get)
        selected.append(best_i)
        remaining.remove(best_i)
    # Return the selected candidate chunks in the order they were selected.
    return [candidate_chunks[i] for i in selected]
