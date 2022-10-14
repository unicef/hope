from django.contrib.admin import TabularInline

from adminfilters.combo import RelatedFieldComboFilter

from hct_mis_api.apps.account.models import User, UserRole
from hct_mis_api.apps.ba_admin.options import BAModelAdmin, BATabularInline


class UserRoleInline(BATabularInline):
    model = UserRole
    extra = 0

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(UserRoleInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "business_area":
            ba = self.admin_site.selected_business_area(request)
            field.queryset = field.queryset.filter(id=ba.id)

        return field


class UserAdmin(BAModelAdmin):
    model = User
    target_field = "user_roles__business_area__slug"
    list_display = ["username", "email", "partner", "is_active"]
    search_fields = ["username", "email"]
    list_filter = (("partner", RelatedFieldComboFilter), "is_active")
    exclude = (
        "password",
        "doap_hash",
        "custom_fields",
        "is_superuser",
        "ad_uuid",
    )
    inlines = [UserRoleInline]


class UserRoleAdmin(BAModelAdmin):
    model = UserRole
    target_field = "business_area__slug"
