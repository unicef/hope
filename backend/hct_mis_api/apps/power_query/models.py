import logging
import pickle

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import JSONField
from django.template import Context, Template
from django.utils import timezone

from sentry_sdk import capture_exception

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.power_query.utils import to_dataset

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


class Query(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="power_queries")
    target = models.ForeignKey(ContentType, on_delete=models.CASCADE, default="")
    code = models.TextField(default="qs=conn.all()", blank=True)
    info = JSONField(default=dict, blank=True)
    query_args = JSONField(default=dict, blank=True)

    error = models.CharField(max_length=400, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Power Queries"
        ordering = ("name",)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.code:
            self.code = "qs=conn.all().order_by('id')"
        self.error = None
        if not update_fields:
            try:
                self.dataset.delete()
            except Dataset.DoesNotExist:
                pass
        super().save(force_insert, force_update, using, update_fields)

    @property
    def ready(self):
        try:
            return self.dataset is not None
        except Dataset.DoesNotExist:
            pass
        return False

    def _invoke(self, query_id):
        query = Query.objects.get(id=query_id)
        result, debug_info = query.execute(persist=False)
        return result, debug_info

    def execute(self, persist=False, query_args=None):
        model = self.target.model_class()
        filters = query_args or {}
        _error = None
        try:
            locals_ = {
                "conn": model._default_manager.using(settings.POWER_QUERY_DB_ALIAS),
                "query": self,
                "query_filters": filters,
                "invoke": self._invoke,
            }

            exec(self.code, globals(), locals_)
            result = locals_.get("result", None)
            debug_info = locals_.get("debug_info", None)

            if persist and result:
                info = {
                    "type": type(result).__name__,
                    "debug_info": debug_info,
                }
                r, __ = Dataset.objects.update_or_create(
                    query=self,
                    defaults={
                        "last_run": timezone.now(),
                        "result": pickle.dumps(result),
                        "info": info,
                    },
                )

            return result, debug_info
        except Exception as e:
            _error = capture_exception(e)
            logger.exception(e)
        finally:
            Query.objects.filter(pk=self.pk).update(error=_error)
        return None, None


class Dataset(models.Model):
    last_run = models.DateTimeField(null=True, blank=True)
    query = models.OneToOneField(Query, on_delete=models.CASCADE)
    result = models.BinaryField(null=True, blank=True)
    info = JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Result of {self.query.name}"

    @property
    def data(self):
        return pickle.loads(self.result)


class Formatter(models.Model):
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


class Report(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    formatter = models.ForeignKey(Formatter, on_delete=models.CASCADE)
    refresh = models.BooleanField(default=False)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="+")
    available_to = models.ManyToManyField(User, blank=True, related_name="+")

    query_args = JSONField(default=dict, blank=True)
    last_run = models.DateTimeField(null=True, blank=True)
    result = models.BinaryField(null=True, blank=True)

    def execute(self, run_query=False):
        if run_query:
            self.query.execute(True)
        try:
            output = self.formatter.render(
                {
                    "dataset": self.query.dataset,
                    "report": "self",
                }
            )
            self.last_run = timezone.now()
            self.result = pickle.dumps(output)
            self.save()
            return output
        except ObjectDoesNotExist:
            pass

    def __str__(self):
        return self.name
