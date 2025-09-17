from django.shortcuts import render
from django.views import View


class BaseHopeTemplate(View):
    def get(self, request):
        # You can pass context here if needed
        return render(request, "example_extended_template.html", {})
