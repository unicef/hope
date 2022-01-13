import pickle

import json
import tablib

from builtins import __build_class__

import logging
from concurrency.utils import fqn

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core import serializers
from django.db import models
from django.db.models import QuerySet
from django.template import Template, Context
from django.utils import timezone
from django.utils.functional import cached_property
from django_celery_beat.models import CrontabSchedule

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.power_query.utils import to_dataset

logger = logging.getLogger(__name__)

mimetype_map = {
    'xls': 'application/vnd.ms-excel',
    'txt': 'text/plain',
    'csv': 'text/csv',
    'html': 'text/html',
    'yaml': 'text/yaml',
    'json': 'application/json',
}


class Query(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='power_queries')
    target = models.ForeignKey(ContentType, on_delete=models.CASCADE, default="")
    code = models.TextField(default="qs=conn.all()", blank=True)
    info = JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Power Queries'
        ordering = ('name',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.code:
            self.code = "qs=conn.all().order_by('id')"
        try:
            self.dataset.delete()
        except Dataset.DoesNotExist:
            pass
        super().save(force_insert, force_update, using, update_fields)

    def execute(self, persist=False):
        model = self.target.model_class()
        # gl = {
        #     "__builtins__": {
        #         "__build_class__": __build_class__,
        #         "__name__": __name__,
        #         "__import__": __import__,
        #         "bytearray": bytearray,
        #         "power_"
        #         "bytes": bytes,
        #         "tablib": tablib,
        #         "complex": complex,
        #         "dict": dict,
        #         "float": float,
        #         "frozenset": frozenset,
        #         "int": int,
        #         "list": list,
        #         "print": print,
        #         "memoryview": memoryview,
        #         "range": range,
        #         "set": set,
        #         "str": str,
        #         "tuple": tuple,
        #     }
        # }
        try:
            locals_ = dict()
            locals_["conn"] = model._default_manager.using('ro')
            locals_["query"] = self
            exec(self.code, globals(), locals_)
            result = locals_.get('result', None)

            if persist:
                info = {'type': type(result).__name__,
                        'fqn': fqn(result),
                        }
                r, __ = Dataset.objects.update_or_create(query=self,
                                                         defaults={
                                                             'last_run': timezone.now(),
                                                             'result': pickle.dumps(result),
                                                             'info': info
                                                         })

            return result
        except Exception as e:
            logger.exception(e)
            raise


class Dataset(models.Model):
    last_run = models.DateTimeField(null=True, blank=True)
    query = models.OneToOneField(Query, on_delete=models.CASCADE)
    result = models.BinaryField(null=True, blank=True)
    info = JSONField(default=dict, blank=True)

    def __str__(self):
        return f'Result of {self.query.name}'

    @property
    def data(self):
        return pickle.loads(self.result)


class Formatter(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    content_type = models.CharField(max_length=5, choices=list(map(list, mimetype_map.items())))
    code = models.TextField()

    def __str__(self):
        return self.name

    def render(self, context):
        if self.content_type == 'xls':
            dt = to_dataset(context['dataset'])
            return dt.export('xls')
        tpl = Template(self.code)
        return tpl.render(Context(context))


class Report(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    formatter = models.ForeignKey(Formatter, on_delete=models.CASCADE)
    refresh = models.BooleanField(default=False)
    notify_to = models.ManyToManyField(User, blank=True)

    last_run = models.DateTimeField(null=True, blank=True)
    result = models.BinaryField(null=True, blank=True)

    def execute(self):
        self.query.execute(True)
        output = self.formatter.render({'dataset': self.query.dataset,
                                        'report': 'self',
                                        })
        self.last_run = timezone.now()
        self.result = pickle.dumps(output)
        self.save()
