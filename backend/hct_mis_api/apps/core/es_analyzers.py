import os

from django.conf import settings
from elasticsearch_dsl import token_filter, analyzer, tokenizer

phonetic_filter = token_filter(
    "my_metaphone", type="phonetic", encoder="double_metaphone", replace=False, langauge_set="common"
)

phonetic_analyzer = analyzer(
    "phonetic",
    tokenizer=tokenizer("standard"),
    filter=["lowercase", phonetic_filter],
)

with open(os.path.join(settings.PROJECT_ROOT, "../data/synonyms.txt"), "r") as synonyms_file:
    synonyms = synonyms_file.readlines()

name_synonym_analyzer_token_filter = token_filter(
    "synonym_tokenfilter",
    "synonym",
    synonyms=synonyms,
)


name_synonym_analyzer = analyzer(
    "text_analyzer",
    tokenizer="standard",
    filter=[
        "lowercase",
        name_synonym_analyzer_token_filter,
    ],
)
