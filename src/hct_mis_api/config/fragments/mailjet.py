from hct_mis_api.config.env import env

MAILJET_API_KEY = env("MAILJET_API_KEY")
MAILJET_SECRET_KEY = env("MAILJET_SECRET_KEY")
CATCH_ALL_EMAIL = env.list("CATCH_ALL_EMAIL")
DEFAULT_EMAIL_DISPLAY = env("DEFAULT_EMAIL_DISPLAY")
DEFAULT_EMAIL = env("DEFAULT_EMAIL")
