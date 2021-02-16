# RDI and Deduplication task

**Registration Data Import and Deduplication process:**

After the successful validation of the uploaded file, the importing process can be started. 

During the RDI process, RegistrationDataImport and RegistrationDataImportDatahub objects are created. 

RegistrationDataImport - objects have almost the same fields and data as RegistrationDataImportDatahub, the difference is that RegistrationDataImport is for Individual and Household models and RegistrationDataImportDatahub is for ImportedIndividual and ImportedHousehold models.

RDI process creates ImportedIndividual and ImportedHousehold objects.

After successful creating of these objects, we are calling search\_index --populate command to add and index ImportedIndividuals to elasticsearch.

**Elasticsearch has two indexes:**

1. individuals: this one holds Individuals objects data \(golden records\)
2. importedindividuals: holds all ImportedIndividuals data ever created

We cannot remove ImportedIndividuals from Postgres and therefore from elasticsearch because we still need to display them in the Registration Data Import Section.

**Deduplication process:**

for each individual, we are calling a query:

```text
"min_score": < MINIMAL SCORE THAT CAN BE CHANGED IN DJANGO ADMIN >,
    "query": {
        "bool": {
            "must": [
                {"dis_max": 
                     {"queries":
                        < fuzzy queries for almost all fields >
                        < match queries for hash_key, birth_day, full_name >
                     }
                }
            ],
            "must_not": [{"match": {"id": {"query": individual.id}}}],
    }
},

# for deduplication in batch we are also using filter to get only 
 ImportedIndividualsDocuments that belongs to the same RegistrationDataImport
```

hash\_key is boosted by 3.0 and full\_name is boosted by 2.0

hash\_key is the individual property that is SHA256 hash created from fields:

* "given\_name",
* "middle\_name",
* "family\_name",
* "sex",
* "birth\_date",
* "phone\_no",
* "phone\_no\_alternative",
* "relationship",

Two rules are applied to check if the individual is duplicate:

* if the score is above the threshold

   or

* if hash\_key is the same for compared individuals

After checking all individuals from the uploaded file, we are changing statuses if they are duplicates or similar and also saving elasticsearch query similarity results to the individual model fields:

* deduplication\_batch\_results
* deduplication\_golden\_record\_results

those are JSON fields and the data that are saved are:

* hit\_id 
* score
* full\_name

