from hct_mis_api.config.env import env

# ELASTICSEARCH SETTINGS
ELASTICSEARCH_DSL_AUTOSYNC = False
ELASTICSEARCH_HOST = env("ELASTICSEARCH_HOST")
ELASTICSEARCH_INDEX_PREFIX = env("ELASTICSEARCH_INDEX_PREFIX", default="")
ELASTICSEARCH_DSL = {
    "default": {"hosts": ELASTICSEARCH_HOST, "timeout": 30},
}
ELASTICSEARCH_BASE_SETTINGS = {"number_of_shards": 1, "number_of_replicas": 0}
