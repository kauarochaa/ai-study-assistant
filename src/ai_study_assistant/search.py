"""Local keyword retrieval, with no API calls or extra dependencies."""

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass

from .documents import DocumentChunk


STOP_WORDS = set(
    "a ao aos as com como da das de do dos e em essa esse esta este eu foi "
    "mais na nas no nos o os ou para pela pelo por qual quais que se ser "
    "sua suas seu seus um uma umas uns voce sao tem sobre".split()
)


def tokenize(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return [word for word in re.findall(r"[a-z0-9]+", normalized) if word not in STOP_WORDS]


@dataclass(frozen=True)
class SearchResult:
    chunk: DocumentChunk
    score: float


class KeywordSearch:
    """Rank matching chunks with BM25; scores are not confidence percentages."""

    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self.chunks = list(chunks)
        self.term_counts = [Counter(tokenize(chunk.text)) for chunk in self.chunks]
        self.lengths = [sum(counts.values()) for counts in self.term_counts]
        self.average_length = sum(self.lengths) / len(self.lengths) if self.lengths else 0
        self.document_frequency = Counter(
            term for counts in self.term_counts for term in counts
        )

    def search(self, question: str, limit: int = 3) -> list[SearchResult]:
        terms = set(tokenize(question))
        if not terms or not self.average_length or limit <= 0:
            return []

        results = []
        for chunk, counts, length in zip(self.chunks, self.term_counts, self.lengths):
            score = 0.0
            for term in terms:
                frequency = counts[term]
                if not frequency:
                    continue
                df = self.document_frequency[term]
                weight = math.log(1 + (len(self.chunks) - df + 0.5) / (df + 0.5))
                denominator = frequency + 1.5 * (0.25 + 0.75 * length / self.average_length)
                score += weight * frequency * 2.5 / denominator

            if score > 0:
                results.append(SearchResult(chunk, score))

        return sorted(results, key=lambda result: result.score, reverse=True)[:limit]
