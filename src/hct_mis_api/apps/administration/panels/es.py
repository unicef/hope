import logging
from typing import Any, Dict, Optional

from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from elasticsearch_dsl.connections import create_connection

from hct_mis_api.apps.utils.elasticsearch_utils import (
    populate_all_indexes,
    rebuild_search_index,
)

logger = logging.getLogger(__name__)


class EsForm(forms.Form):
    ACTIONS = [
        ("info", "info()"),
        ("test_connection", "test_connection()"),
        ("rebuild_search_index", "rebuild_search_index()"),
        ("populate_all_indexes", "populate_all_indexes()"),
    ]
    action = forms.ChoiceField(choices=ACTIONS, widget=forms.RadioSelect)


class ElasticsearchPanel:
    __name__ = "Elasticsearch"

    def rebuild_search_index(self, request: HttpRequest) -> None:
        rebuild_search_index()

    def __call__(self, model_admin: Any, request: HttpRequest, extra_context: Optional[Dict] = None) -> HttpResponse:
        context = model_admin.each_context(request)
        context["config"] = {
            "ELASTICSEARCH_HOST": settings.ELASTICSEARCH_HOST,
            "ELASTICSEARCH_DSL_AUTOSYNC": settings.ELASTICSEARCH_DSL_AUTOSYNC,
            "ELASTICSEARCH_INDEX_PREFIX": settings.ELASTICSEARCH_INDEX_PREFIX,
        }
        logs = {}
        if request.method == "POST":
            form = EsForm(request.POST)
            if form.is_valid():
                opt = form.cleaned_data["action"]
                try:
                    if opt == "test_connection":
                        conn = create_connection()
                        conn.ping()
                    elif opt == "info":
                        conn = create_connection()
                        logs = conn.info()
                    elif opt == "rebuild_search_index":
                        rebuild_search_index()
                    elif opt == "populate_all_indexes":
                        populate_all_indexes()
                    else:
                        raise ValueError(opt)
                except Exception as exc:
                    logger.warning(exc)
                    messages.add_message(request, messages.ERROR, f"{exc.__class__.__name__}: {exc}")
        else:
            form = EsForm()

        context["form"] = form
        context["logs"] = logs
        return render(request, "administration/panels/elasticsearch.html", context)


panel_elasticsearch = ElasticsearchPanel()

panel_elasticsearch.verbose_name = _("Elasticsearch")
panel_elasticsearch.url_name = "es"
