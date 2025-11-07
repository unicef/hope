from hope.config.env import env

STORAGES = {
    "default": env.storage("FILE_STORAGE_MEDIA"),
    "staticfiles": env.storage("FILE_STORAGE_STATIC"),
}
