from hope.config.env import env

STREAMING = {
    "BROKER_URL": env("CELERY_BROKER_URL"),
    "QUEUES": {
        "hope_live": {
            "name": "hope_live",
            "binding_keys": ["rdi.*", "payment.*", "payment_plan.*", "program.*"],
        },
    },
    "CLIENT_NAME": "hope_live",
    "RETRY_COUNT": 3,
    "RETRY_DELAY": 1,
    "MESSAGE_TTL": 60,  # 60 seconds
    "MANAGER_CLASS": "streaming.manager.ChangeManager",
    "LISTEN_CALLBACK": "streaming.callbacks.default_callback",
}
