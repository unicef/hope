from elasticsearch_dsl import token_filter, analyzer, tokenizer


phonetic_filter = token_filter("my_metaphone", type="phonetic", encoder="metaphone", replace=False,)

phonetic_analyzer = analyzer("phonetic", tokenizer=tokenizer("standard"), filter=["lowercase", phonetic_filter],)
