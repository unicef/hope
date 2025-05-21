from hct_mis_api.config.settings import DEBUG

FLAGS_STATE_LOGGING = DEBUG
FLAGS = {
    "DEVELOP_DEBUG_TOOLBAR": [],
    "SILK_MIDDLEWARE": [],
    "FRONT_DOOR_BYPASS": [],
    "ALLOW_ACCOUNTABILITY_MODULE": [{"condition": "boolean", "value": False}],
    "NEW_RECORD_MODEL": [{"condition": "boolean", "value": False}],
}
