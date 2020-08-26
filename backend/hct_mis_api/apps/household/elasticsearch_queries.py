from typing import List, Union

from elasticsearch_dsl.query import MoreLikeThis

from household.documents import IndividualDocument
from registration_datahub.documents import ImportedIndividualDocument

"""
This file contains some test queries to play with ElasticSearch,
the file will be removed in the future
"""
query = IndividualDocument.search().query(
    MoreLikeThis(like="Lroi", min_term_freq=1, fields=["given_name", "full_name"], analyzer="phonetic",)
)

query2 = IndividualDocument.search().query(
    MoreLikeThis(like="Lori", min_term_freq=1, fields=["given_name", "full_name"], analyzer="phonetic",)
)

query3 = ImportedIndividualDocument.search().query(
    MoreLikeThis(
        like={"_id": "170fa724-51f2-44df-a5be-df83dcf624da", "_index": "importedindividuals",},
        min_term_freq=1,
        fields=["given_name", "full_name"],
        analyzer="phonetic",
        minimum_should_match="75%",
    )
)


def get_similar_objects(
    document: Union[ImportedIndividualDocument, IndividualDocument],
    object_id: str,
    fields: List[str],
    threshold: str = "75%",
):
    query = document.search().query(
        MoreLikeThis(
            like={"_id": object_id, "_index": document._index._name,},
            min_term_freq=1,
            fields=fields,
            analyzer="phonetic",
            minimum_should_match=threshold,
        )
    )

    return query.execute()
