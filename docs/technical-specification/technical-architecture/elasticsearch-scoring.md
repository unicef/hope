# Elasticsearch Scoring

**How scoring works:**

Before Elasticsearch starts scoring documents, it first reduces the candidate documents down by applying a boolean test - does the document match the query? Once the results that match are retrieved, the score they receive will determine how they are rank-ordered for relevancy.

The scoring of a document is determined based on the field matches from the query specified and any additional configurations that are applied to the search.

Elasticsearch uses Lucene's [Practical Scoring Function](https://www.elastic.co/guide/en/elasticsearch/guide/current/practical-scoring-function.html). This is a similarity model based on Term Frequency \(tf\) and Inverse Document Frequency \(idf\) that also uses the Vector Space Model \(vsm\) for multi-term queries. 

**score\(q,d\)** =  
             queryNorm\(q\)  
           \* coord\(q,d\)  
           \* SUM \(  
                 tf\(t in d\),  
                 idf\(t\)²,  
                 t.getBoost\(\),  
                 norm\(t,d\)  
              \) \(t in q\)

* score\(q,d\) is the relevance score of document d for query q.
* queryNorm\(q\) is the query normalization factor.
* coord\(q,d\) is the coordination factor.
* The sum of the weights for each term t in the query q for document d.
  * tf\(t in d\) is the term frequency for term t in document d.
  * idf\(t\) is the inverse document frequency for term t.
  * t.getBoost\(\) is the boost that has been applied to the query.
  * norm\(t,d\) is the field-length norm, combined with the index-time field-level boost if any.

**More information about scoring**: [https://www.elastic.co/guide/en/elasticsearch/guide/current/practical-scoring-function.html](https://www.elastic.co/guide/en/elasticsearch/guide/current/practical-scoring-function.html)

**Algorithm \(in Lucence\):**

[https://lucene.apache.org/core/3\_5\_0/scoring.html\#Algorithm](https://lucene.apache.org/core/3_5_0/scoring.html#Algorithm)

