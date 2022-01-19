from django.conf import settings
from django.db.models import QuerySet
from django.utils.safestring import mark_safe

import tablib


def to_dataset(result):
    if isinstance(result, QuerySet):
        data = tablib.Dataset()
        fields = [field.name for field in result.model._meta.fields]
        data.headers = fields
        for obj in result.all():
            data.append([getattr(obj, f) for f in fields])
    elif isinstance(result, tablib.Dataset):
        data = result
    elif isinstance(result, dict):
        data = result
    else:
        raise ValueError(f"{result} ({type(result)}")
    return data


def get_sentry_url(event_id, html=False):
    url = f"{settings.SENTRY_URL}?query={event_id}"
    if html:
        return mark_safe('<a href="{url}" target="_sentry" >View on Sentry<a/>')
    return url
