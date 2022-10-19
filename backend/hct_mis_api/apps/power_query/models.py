import itertools
import logging
import pickle

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import JSONField
from django.template import Context, Template
from django.urls import reverse
from django.utils import timezone
from django.utils.datetime_safe import strftime
from django.utils.functional import cached_property
from django.utils.text import slugify

from natural_keys import NaturalKeyModel
from sentry_sdk import capture_exception

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.power_query.defaults import SYSTEM_PARAMETRIZER
from hct_mis_api.apps.power_query.exceptions import QueryRunError
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

    def get_matrix(self) -> list[dict]:
        product = list(itertools.product(*self.value.values()))
        return [dict(zip(self.value.keys(), e)) for e in product]

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.code:
            self.code = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    def refresh(self):
        if self.code in SYSTEM_PARAMETRIZER:
            self.value = SYSTEM_PARAMETRIZER[self.code]["value"]()
            self.save()

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
    sentry_error_id = models.CharField(max_length=400, blank=True, null=True)
    error_message = models.CharField(max_length=400, blank=True, null=True)

    active = models.BooleanField(default=True)
    refresh_daily = models.BooleanField(default=False)

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

    def _invoke(self, query_id, arguments):
        query = Query.objects.get(id=query_id)
        result = query.run(persist=False, arguments=arguments)
        return result

    def update_results(self, results):
        self.info["last_run_results"] = results
        self.save()

    def execute_matrix(self, persist=True, **kwargs) -> "[Dataset]":
        if self.parametrizer:
            args = self.parametrizer.get_matrix()
        else:
            args = [{}]
        if not args:
            raise ValueError("No valid arguments provided")
        results = {"timestamp": strftime(timezone.now(), "%Y-%m-%d %H:%M")}
        with transaction.atomic():
            transaction.on_commit(lambda: self.update_results(results))
            for a in args:
                try:
                    dataset, __ = self.run(persist, a)
                    results[str(a)] = dataset.pk
                except QueryRunError as e:
                    results[str(a)] = e
            self.datasets.exclude(pk__in=[dpk for dpk in results.values() if isinstance(dpk, int)]).delete()
        return results

    def run(self, persist=False, arguments: dict = None) -> "[Dataset, dict]":
        model = self.target.model_class()
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
            result = locals_.get("result", None)
            extra = locals_.get("extra", None)

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
                return_value = dataset, extra
            else:
                return_value = result, extra
        except Exception as e:
            logger.exception(e)
            sentry_error_id = capture_exception(e)
            raise QueryRunError(e, sentry_error_id)
        return return_value


class Dataset(NaturalKeyModel, models.Model):
    hash = models.CharField(unique=True, max_length=200, editable=False)
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
    document_title = models.CharField(max_length=255, blank=True, null=True)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    formatter = models.ForeignKey(Formatter, on_delete=models.CASCADE)
    refresh_daily = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="+")
    limit_access_to = models.ManyToManyField(User, blank=True, related_name="+")

    last_run = models.DateTimeField(null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.document_title:
            self.document_title = self.name
        super().save(force_insert, force_update, using, update_fields)

    def execute(self, run_query=False):
        query: Query = self.query
        result = []
        if run_query:
            query.execute_matrix()
        for dataset in query.datasets.all():
            if not dataset.size:
                continue
            try:
                context = {**dataset.arguments, **(pickle.loads(dataset.extra) or {})}
                title = self.document_title % context
                output = self.formatter.render({"dataset": dataset, "report": self, "title": title, "context": context})
                res, __ = ReportDocument.objects.update_or_create(
                    report=self,
                    dataset=dataset,
                    defaults={
                        "title": title,
                        "content_type": self.formatter.content_type,
                        "output": pickle.dumps(output),
                        "arguments": dataset.arguments,
                    },
                )
                result.append([dataset.pk, len(res.output)])
            except Exception as e:
                logger.exception(e)
                result.append([dataset.pk, e])
        if not result:
            result = ["No Dataset available"]
        return result

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("power_query:report", args=[self.pk])


class ReportDocumentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("report")


class ReportDocument(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=300)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="documents")
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    output = models.BinaryField(null=True, blank=True)
    arguments = models.JSONField(default=dict)
    limit_access_to = models.ManyToManyField(User, blank=True, related_name="+")
    content_type = models.CharField(max_length=5, choices=list(map(list, mimetype_map.items())))

    objects = ReportDocumentManager()

    class Meta:
        unique_together = ("report", "dataset")

    def __str__(self):
        return self.title

    @cached_property
    def data(self):
        return pickle.loads(self.output)

    @cached_property
    def size(self):
        return len(self.output)

    def get_absolute_url(self):
        return reverse("power_query:document", args=[self.report.pk, self.pk])
