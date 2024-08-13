from dataclasses import dataclass


@dataclass
class SimilarityIndividual:
    id: str
    file: str


@dataclass
class SimilarityPair:
    similarity_score: float
    first_individual: SimilarityIndividual
    second_individual: SimilarityIndividual
