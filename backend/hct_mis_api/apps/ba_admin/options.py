from functools import update_wrapper

from django.forms import MediaDefiningClass
from django.views.generic import RedirectView

from smart_admin.modeladmin import SmartModelAdmin

model_admin_registry = []


class AutoRegisterMetaClass(MediaDefiningClass):
    def __new__(mcs, class_name, bases, attrs):
        new_class = super().__new__(mcs, class_name, bases, attrs)
        if new_class.model:
            model_admin_registry.append(new_class)
        return new_class


class BAModelAdmin(SmartModelAdmin, metaclass=AutoRegisterMetaClass):
    model = None
    target_field = None
    change_list_template = "ba_admin/change_list.html"
    change_form_template = "ba_admin/change_form.html"

    def get_business_area_filter(self, request):
        return {self.target_field: self.admin_site.selected_business_area(request).slug}

    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs.filter(**self.get_business_area_filter(request)).distinct()

    def get_urls(self):
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        return [
            path("", wrap(self.changelist_view), name="%s_%s_changelist" % info),
            # path('add/', wrap(self.add_view), name='%s_%s_add' % info),
            # path('<path:object_id>/history/', wrap(self.history_view), name='%s_%s_history' % info),
            # path('<path:object_id>/delete/', wrap(self.delete_view), name='%s_%s_delete' % info),
            path("<path:object_id>/change/", wrap(self.change_view), name="%s_%s_change" % info),
            # For backwards compatibility (was the change url before 1.9)
            path(
                "<path:object_id>/",
                wrap(RedirectView.as_view(pattern_name="%s:%s_%s_change" % ((self.admin_site.name,) + info))),
            ),
        ]

    def has_module_permission(self, request):
        return True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True
