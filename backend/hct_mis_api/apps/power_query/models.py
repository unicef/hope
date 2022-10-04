import itertools
import logging
import pickle
from typing import Optional

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import JSONField
from django.template import Context, Template
from django.utils import timezone
from django.utils.text import slugify

from natural_keys import NaturalKeyModel
from sentry_sdk import capture_exception

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.power_query.utils import sizeof, to_dataset

logger = logging.getLogger(__name__)

mimetype_map = {
    "csv": "text/csv",
    "html": "text/html",
    "json": "application/json",
    "txt": "text/plain",
    "xls": "application/vnd.ms-excel",
    "xml": "application/xml",
    "yaml": "text/yaml",
}


def validate_queryargs(value):
    try:
        if not isinstance(value, dict):
            raise ValidationError("QueryArgs must be a dict")
        product = list(itertools.product(*value.values()))
        [dict(zip(value.keys(), e)) for e in product]
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError("%(exc)s: " "%(value)s is not a valid QueryArgs", params={"value": value, "exc": e})


class Parametrizer(NaturalKeyModel, models.Model):
    code = models.SlugField(max_length=255, unique=True, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(
        max_length=255,
        null=True,
        blank=True,
    )
    value = models.JSONField(default=dict, blank=False, validators=[validate_queryargs])
    system = models.BooleanField(blank=True, default=False, editable=False)

    class Meta:
        verbose_name_plural = "Arguments"
        verbose_name = "Arguments"

    def clean(self):
        validate_queryargs(self.value)

    def get_matrix(self):
        product = list(itertools.product(*self.value.values()))
        return [dict(zip(self.value.keys(), e)) for e in product]

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.code:
            self.code = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class Query(NaturalKeyModel, models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="power_queries")
    target = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    code = models.TextField(default="qs=conn.all()", blank=True)
    info = JSONField(default=dict, blank=True)
    parametrizer = models.ForeignKey(Parametrizer, on_delete=models.CASCADE, blank=True, null=True)
    error = models.CharField(max_length=400, blank=True, null=True)

    def __str__(self):
        return self.name or ""

    class Meta:
        verbose_name_plural = "Power Queries"
        ordering = ("name",)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.code:
            self.code = "qs=conn.all().order_by('id')"
        self.error = None
        super().save(force_insert, force_update, using, update_fields)

    def execute_matrix(self, persist=False, **kwargs) -> "[Dataset]":
        if self.parametrizer:
            args = self.parametrizer.get_matrix()
        else:
            args = []
        results = []
        for a in args:
            try:
                pk = self.run(persist, a)
                results.append(pk)
            except Exception as e:
                results.append(e)

        return results

    def complete(self) -> "Dataset":
        pass

    def run(self, persist=False, query_args=None) -> "Optional[Dataset]":
        model = self.target.model_class()
        _error = None
        return_value = None
        try:
            locals_ = {
                "conn": model._default_manager.using(settings.POWER_QUERY_DB_ALIAS),
                "query": self,
                "args": query_args,
                "arguments": query_args,
            }

            exec(self.code, globals(), locals_)
            result = locals_.get("result", None)
            if persist:
                info = {"type": type(result).__name__, "size": sizeof(len(result)), "arguments": query_args}
                r, __ = Dataset.objects.update_or_create(
                    query=self,
                    info=info,
                    defaults={
                        "last_run": timezone.now(),
                        "result": pickle.dumps(result),
                    },
                )
                return_value = r.pk
        except Exception as e:
            _error = capture_exception(e)
            logger.exception(e)
        finally:
            Query.objects.filter(pk=self.pk).update(error=_error)
        return return_value


class Dataset(models.Model):
    last_run = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=100)
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name="datasets")
    result = models.BinaryField(null=True, blank=True)
    info = JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Result of {self.query.name}"

    @property
    def data(self):
        return pickle.loads(self.result)

    @property
    def size(self):
        return self.info.get("size")


class Formatter(NaturalKeyModel, models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    content_type = models.CharField(max_length=5, choices=list(map(list, mimetype_map.items())))
    code = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def render(self, context):
        if self.content_type == "xls":
            dt = to_dataset(context["dataset"].data)
            return dt.export("xls")
        if self.code:
            tpl = Template(self.code)
        elif self.content_type == "json":
            dt = to_dataset(context["dataset"].data)
            return dt.export("json")
        elif self.content_type == "yaml":
            dt = to_dataset(context["dataset"].data)
            return dt.export("yaml")
        else:
            raise ValueError("Unable to render")
        return tpl.render(Context(context))


class Report(NaturalKeyModel, models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    formatter = models.ForeignKey(Formatter, on_delete=models.CASCADE)
    refresh = models.BooleanField(default=False)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="+")
    limit_access_to = models.ManyToManyField(User, blank=True, related_name="+")

    last_run = models.DateTimeField(null=True, blank=True)

    def execute(self, run_query=False):
        query: Query = self.query
        result = []
        for dataset in query.datasets.all():
            try:
                output = self.formatter.render(
                    {
                        "dataset": dataset,
                        "report": "self",
                    }
                )
                res, __ = ReportResult.objects.update_or_create(report=self, dataset=dataset)
                res.last_run = timezone.now()
                res.output = pickle.dumps(output)
                res.save()
                result.append([res.pk, len(res.output)])
            except Exception as e:
                result.append(e)
        return result

    def __str__(self):
        return self.name


class ReportResult(NaturalKeyModel, models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    output = models.BinaryField(null=True, blank=True)
