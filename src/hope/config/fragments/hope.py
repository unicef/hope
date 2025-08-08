from hope.config.env import env

DEFAULT_EMPTY_PARTNER = "Default Empty Partner"


GRIEVANCE_ONE_UPLOAD_MAX_MEMORY_SIZE = 3 * 1024 * 1024
GRIEVANCE_UPLOAD_CONTENT_TYPES = (
    "image/jpeg",
    "image/png",
    "image/tiff",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)

SANCTION_LIST_CC_MAIL = env("SANCTION_LIST_CC_MAIL")

EXCHANGE_RATE_CACHE_EXPIRY = env.int("EXCHANGE_RATE_CACHE_EXPIRY")
USE_DUMMY_EXCHANGE_RATES = env("USE_DUMMY_EXCHANGE_RATES") == "yes"
EXCHANGE_RATES_API_URL = env("EXCHANGE_RATES_API_URL")
EXCHANGE_RATES_API_KEY = env("EXCHANGE_RATES_API_KEY")
