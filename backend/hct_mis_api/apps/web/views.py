from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def react_main(request: HttpRequest) -> HttpResponse:
    return render(request, "web/index.html")
