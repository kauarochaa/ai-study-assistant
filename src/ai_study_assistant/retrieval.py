"""Combine semantic and exact-term matches, keeping nearby context."""
from .search import KeywordSearch, SearchResult

MIN_SEMANTIC_SCORE = 0.30


def retrieve(question, chunks, semantic_results, limit=8):
    if not question.strip() or limit <= 0:
        return []
    scores = {}
    semantic_results = [result for result in semantic_results if result.score >= MIN_SEMANTIC_SCORE]
    for ranked in (semantic_results, KeywordSearch(chunks).search(question, limit=4)):
        for rank, result in enumerate(ranked, 1):
            scores[result.chunk] = scores.get(result.chunk, 0) + 1 / (60 + rank)
    seeds = sorted(scores, key=scores.get, reverse=True)[:3]
    selected = []
    lookup = {(chunk.source, chunk.page, chunk.index): chunk for chunk in chunks}
    # Include original matches first, then adjacent chunks that may complete a definition.
    for chunk in seeds:
        selected.append(SearchResult(chunk, scores[chunk]))
    seen = set(seeds)
    for chunk in seeds:
        for index in (chunk.index - 1, chunk.index + 1):
            nearby = lookup.get((chunk.source, chunk.page, index))
            if nearby is not None and nearby not in seen:
                selected.append(SearchResult(nearby, scores[chunk]))
                seen.add(nearby)
    return selected[:limit]
