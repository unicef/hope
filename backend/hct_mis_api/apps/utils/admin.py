from django.contrib import admin
from django.template.response import TemplateResponse

from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin, _confirm_action
from smart_admin.mixins import DisplayAllMixin as SmartDisplayAllMixin


class HOPEModelAdminBase(SmartDisplayAllMixin, admin.ModelAdmin):
    list_per_page = 50

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj)


class LastSyncDateResetMixin(ExtraUrlMixin):
    @button()
    def reset_sync_date(self, request):
        if request.method == "POST":
            self.get_queryset(request).update(last_sync_at=None)
        else:
            return _confirm_action(
                self,
                request,
                self.reset_sync_date,
                "Continuing will reset all records last_sync_date field.",
                "Successfully executed",
                title="aaaaa",
            )

    @button(label="reset sync date")
    def reset_sync_date_single(self, request, pk):
        if request.method == "POST":
            self.get_queryset(request).filter(id=pk).update(last_sync_at=None)
        else:
            return _confirm_action(
                self,
                request,
                self.reset_sync_date,
                "Continuing will reset last_sync_date field.",
                "Successfully executed",
            )


def get_related(user, field):
    info = {
        "to": field.model._meta.model_name,
        "field_name": field.name,
    }

    if field.related_name:
        related_attr = getattr(user, field.related_name)
    else:
        related_attr = getattr(user, f"{field.name}_set")

    if hasattr(related_attr, "all") and callable(related_attr.all):
        related = related_attr.all()
        opts = related_attr.model._meta
        info["related_name"] = opts.verbose_name
    else:
        opts = related_attr._meta
        related = [related_attr]
        info["related_name"] = opts.verbose_name
    info["data"] = related

    return info


class LinkedObjectMixin(ExtraUrlMixin):
    linked_objects_template = None

    def get_ignored_linked_objects(self):
        return []

    @button()
    def linked_objects(self, request, pk):
        ignored = self.get_ignored_linked_objects()
        opts = self.model._meta
        app_label = opts.app_label
        context = self.get_common_context(request, pk, title="linked objects")
        reverse = []
        for f in self.model._meta.get_fields():
            if f.auto_created and not f.concrete and not f.name in ignored:
                reverse.append(f)
        # context["reverse"] = [get_related(user, f ) for f in reverse]
        context["reverse"] = sorted(
            [get_related(context["original"], f) for f in reverse], key=lambda x: x["related_name"].lower()
        )

        return TemplateResponse(
            request,
            self.linked_objects_template
            or [
                "admin/%s/%s/linked_objects.html" % (app_label, opts.model_name),
                "admin/%s/linked_objects.html" % app_label,
                "admin/linked_objects.html",
            ],
            context,
        )
