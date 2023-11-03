from typing import Any, Dict, List

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import TemplateView


class UniversalTableView(TemplateView):
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        table_context = self.get_table_context()
        return {**context, **table_context}

    def get_queryset(self):
        raise NotImplementedError

    def get_headers(self) -> List[str]:
        raise NotImplementedError

    def get_table_context(self) -> Dict[str, Any]:
        request = self.request
        queryset = self.get_queryset()
        page_number = request.GET.get("page", 1)
        page_size = request.GET.get("page-size", 10)
        paginator = Paginator(queryset, page_size)
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        query_params = request.GET.copy()
        query_params.pop("page", None)
        return {"page": page, "query_params": query_params, "headers": self.get_headers(), "page_size": int(page_size)}