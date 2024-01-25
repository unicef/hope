from typing import TYPE_CHECKING

from django.shortcuts import render

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def react_main(request: HttpRequest) -> HttpResponse:
    return render(request, "web/index.html")
