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
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.power_query.utils import dict_hash, to_dataset

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

    def _invoke(self, query_id):
        query = Query.objects.get(id=query_id)
        result, debug_info = query.run(persist=False)
        return result, debug_info

    def execute_matrix(self, persist=False, **kwargs) -> "[Dataset]":
        if self.parametrizer:
            args = self.parametrizer.get_matrix()
        else:
            args = []
        results = []
        for a in args:
            try:
                dataset = self.run(persist, a)
                results.append(dataset)
            except Exception as e:
                results.append(e)
        self.datasets.exclude(pk__in=[d.pk for d in results if d]).delete()
        return results

    def run(self, persist=False, arguments=None) -> "Optional[Dataset]":
        model = self.target.model_class()
        _error = None
        return_value = None
        connections = {
            f"{model._meta.object_name}Manager": model._default_manager.using(settings.POWER_QUERY_DB_ALIAS)
            for model in [BusinessArea, User]
        }

        try:
            locals_ = {
                "conn": model._default_manager.using(settings.POWER_QUERY_DB_ALIAS),
                "query": self,
                "args": arguments,
                "arguments": arguments,
                "invoke": self._invoke,
                **connections,
            }

            exec(self.code, globals(), locals_)
            result = locals_.get("queryset", None)
            extra = locals_.get("extra", None)
            debug_info = locals_.get("debug_info", None)
            if persist:
                info = {
                    "type": type(result).__name__,
                    "arguments": arguments,
                }
                dataset, __ = Dataset.objects.update_or_create(
                    query=self,
                    hash=dict_hash({"query": self.pk, **arguments}),
                    defaults={
                        "info": info,
                        "last_run": timezone.now(),
                        "value": pickle.dumps(result),
                        "extra": pickle.dumps(extra),
                    },
                )
                return_value = dataset
            else:
                return_value = (result, debug_info)
        except Exception as e:
            _error = capture_exception(e)
            logger.exception(e)
        finally:
            Query.objects.filter(pk=self.pk).update(error=_error)
        return return_value


class Dataset(models.Model):
    hash = models.CharField(unique=True, max_length=200)
    last_run = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=100)
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name="datasets")
    value = models.BinaryField(null=True, blank=True)
    info = JSONField(default=dict, blank=True)
    extra = models.BinaryField(null=True, blank=True, help_text="Any other attribute to pass to the formatter")

    def __str__(self):
        return f"Result of {self.query.name} {self.arguments}"

    @property
    def data(self):
        return pickle.loads(self.value)

    @property
    def size(self):
        return len(self.value)

    @property
    def arguments(self):
        return self.info.get("arguments", {})


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
                        "arguments": dataset.arguments,
                    }
                )
                title = self.name % {**dataset.arguments, **pickle.loads(dataset.extra)}
                res, __ = ReportResult.objects.update_or_create(
                    report=self, title=title, dataset=dataset, output=pickle.dumps(output), arguments=dataset.arguments
                )
                result.append([res.pk, len(res.output)])
            except Exception as e:
                result.append(e)
        return result

    def __str__(self):
        return self.name


class ReportResultManager(models.Manager):
    pass


class ReportResult(NaturalKeyModel, models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=300)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    output = models.BinaryField(null=True, blank=True)
    arguments = models.JSONField(default=dict)
    limit_access_to = models.ManyToManyField(User, blank=True, related_name="+")

    objects = ReportResultManager()

    class Meta:
        unique_together = ("report", "dataset")
