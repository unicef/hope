import tablib
from django.db.models import QuerySet


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
        raise ValueError(result)
    return data

