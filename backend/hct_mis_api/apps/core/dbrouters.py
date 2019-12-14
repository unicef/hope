from django.conf import settings


class DbRouter(object):
    @staticmethod
    def select_db(model):
        db = settings.DATABASE_APPS_MAPPING.get(model._meta.app_label)
        if db is not None:
            return db
        return None

    def db_for_read(self, model, **hints):
        return DbRouter.select_db(model)

    def db_for_write(self, model, **hints):
        return DbRouter.select_db(model)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'default' and app_label not in settings.DATABASE_APPS_MAPPING:
            return True
        mapped_db = settings.DATABASE_APPS_MAPPING.get(app_label)
        return mapped_db == db
