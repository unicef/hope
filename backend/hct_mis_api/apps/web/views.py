from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache


@never_cache
def react_main(request: HttpRequest) -> HttpResponse:
    return render(request, "web/index.html")
