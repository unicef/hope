from elasticsearch_dsl.query import MoreLikeThis

from household.documents import IndividualDocument


"""
This file contains some test queries to play with ElasticSearch,
the file will be removed in the future
"""
query = IndividualDocument.search().query(
    MoreLikeThis(
        like="Lroi",
        min_term_freq=1,
        fields=["given_name", "full_name"],
        analyzer="phonetic",
    )
)

query2 = IndividualDocument.search().query(
    MoreLikeThis(
        like="Lori",
        min_term_freq=1,
        fields=["given_name", "full_name"],
        analyzer="phonetic",
    )
)

