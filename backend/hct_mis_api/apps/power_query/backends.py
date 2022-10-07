from django.contrib.auth.backends import BaseBackend

from .models import Query, Report, ReportDocument


class PowerQueryBackend(BaseBackend):
    def has_perm(self, user_obj, perm, obj=None):
        if isinstance(obj, Report):
            if obj.owner == user_obj:
                return True
        elif isinstance(obj, ReportDocument):
            if obj.report.owner == user_obj:
                return True
        return None
