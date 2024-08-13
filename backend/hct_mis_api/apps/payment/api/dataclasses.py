from dataclasses import dataclass


@dataclass
class SimilarityPair:
    similarity_score: float  # TODO MB this is missing on dedup engine side
    first: str
    second: str
