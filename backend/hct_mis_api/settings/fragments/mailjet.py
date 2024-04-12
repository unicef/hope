from hct_mis_api.settings.env import env

MAILJET_API_KEY = env("MAILJET_API_KEY")
MAILJET_SECRET_KEY = env("MAILJET_SECRET_KEY")
CATCH_ALL_EMAIL = env("CATCH_ALL_EMAIL", default="")