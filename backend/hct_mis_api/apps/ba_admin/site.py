from functools import update_wrapper

from django.shortcuts import redirect
from django.template.response import TemplateResponse

from smart_admin.site import SmartAdminSite

from ..core.models import BusinessArea
from .forms import SelectBusinessAreaForm


class BusinessAreaAdminSite(SmartAdminSite):
    site_title = "----"
    site_header = "kkkk"
    index_title = "Control Panel"
    enable_nav_sidebar = False

    index_template = "ba_admin/index.html"
    smart_index_template = "ba_admin/smart_index.html"

    ba_cookie_name = "selected_ba"
    app_index_template = "ba_admin/app_index.html"

    def __init__(self, name="ba_admin"):
        super().__init__(name)

    def login(self, request, extra_context=None):
        return super().login(request, extra_context)

    def select_ba(self, request):
        context = self.each_context(request)
        if request.method == "POST":
            form = SelectBusinessAreaForm(request.POST, user=request.user)
            if form.is_valid():
                response = redirect(f"{self.name}:index")
                response.set_cookie(self.ba_cookie_name, form.cleaned_data["business_area"].slug)
                return response
        else:
            form = SelectBusinessAreaForm(user=request.user)
        context["form"] = form
        return TemplateResponse(request, "ba_admin/select_ba.html", context)

    def get_urls(self):
        from django.urls import path

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)

            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        urlpatterns = [path("select/", wrap(self.select_ba), name="select_ba")]
        urlpatterns += super().get_urls()

        return urlpatterns

    def get_smart_settings(self, request):
        return {"BOOKMARKS": [], "ANYUSER_LOG": True}

    def index(self, request, extra_context=None):
        if not self.selected_business_area(request):
            return redirect(f"{self.name}:select_ba")
        return super().index(request, extra_context)

    def selected_business_area(self, request):
        try:
            cookie_value = request.COOKIES.get(self.ba_cookie_name)
            return BusinessArea.objects.get(slug=cookie_value)
        except BusinessArea.DoesNotExist:
            return ""

    def each_context(self, request):
        selected_business_area = self.selected_business_area(request)
        ret = super().each_context(request)
        ret["bookmarks"] = []
        ret["site_title"] = "site_title"
        ret["site_header"] = f"{selected_business_area} Control Panel"
        ret["site_name"] = self.name
        ret["site_url"] = "site_url"
        ret["selected_business_area"] = selected_business_area
        ret["ba_form"] = SelectBusinessAreaForm(initial={"business_area": selected_business_area}, user=request.user)
        return ret

    def register(self, admin_class=None, **options):
        self._registry[admin_class.model] = admin_class(admin_class.model, self)

    def has_permission(self, request):
        return request.user.is_active

    def is_smart_enabled(self, request):
        return True


ba_site = BusinessAreaAdminSite()
