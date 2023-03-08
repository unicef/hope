from typing import Any, Optional

from django.conf import settings
from django.db.models import Model


class DbRouter:
    @staticmethod
    def select_db(model: Model) -> Optional[str]:
        if model._meta.proxy:
            model = model._meta.proxy_for_model
        # if f"{model._meta.app_label}." == "mis_datahub.AuroraRecord":
        #     return settings.DATABASE_APPS_MAPPING.get(model._meta.app_label)
        return settings.DATABASE_APPS_MAPPING.get(model._meta.app_label)

    def db_for_read(self, model: Model, **hints: Any) -> Optional[str]:
        return DbRouter.select_db(model)

    def db_for_write(self, model: Model, **hints: Any) -> Optional[str]:
        return DbRouter.select_db(model)

    def allow_migrate(self, db: str, app_label: str, model_name: Optional[str] = None, **hints: Any) -> bool:
        if db == "ro":
            return False
        if db == "default" and app_label not in settings.DATABASE_APPS_MAPPING:
            return True

        mapped_db = settings.DATABASE_APPS_MAPPING.get(app_label)
        return mapped_db == db
