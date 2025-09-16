from django.shortcuts import render
from django.views import View


class CustomTemplateView(View):
    def get(self, request):
        # You can pass context here if needed
        return render(request, "custom_template.html", {})
