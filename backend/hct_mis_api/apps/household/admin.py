from django.contrib import admin

from household.models import (
    Household,
    Individual,
    DocumentType,
    Document,
    Agency,
)


@admin.register(Agency)
class AgencyTypeAdmin(admin.ModelAdmin):
    list_display = ("label", "type")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("document_number", "type", "individual")


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ("label", "country")


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ("id", "size", "country", "head_of_household")


@admin.register(Individual)
class IndividualAdmin(admin.ModelAdmin):
    list_display = (
        "given_name",
        "family_name",
        "sex",
        "relationship",
        "birth_date",
    )
