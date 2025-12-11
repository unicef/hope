from rest_framework import serializers

from hope.apps.sanction_list.models import (
    SanctionListIndividual,
    SanctionListIndividualDateOfBirth,
    SanctionListIndividualDocument,
)


class SanctionListIndividualDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SanctionListIndividualDocument
        fields = (
            "id",
            "type_of_document",
            "document_number",
        )


class SanctionListIndividualDateOfBirthSerializer(serializers.ModelSerializer):
    class Meta:
        model = SanctionListIndividualDateOfBirth
        fields = (
            "id",
            "date",
        )


class SanctionListIndividualSerializer(serializers.ModelSerializer):
    documents = SanctionListIndividualDocumentSerializer(many=True)
    dates_of_birth = SanctionListIndividualDateOfBirthSerializer(many=True)
    sanction_list_name = serializers.CharField(source="sanction_list.name")

    class Meta:
        model = SanctionListIndividual
        fields = (
            "id",
            "full_name",
            "reference_number",
            "documents",
            "dates_of_birth",
            "sanction_list_name",
        )


class CheckAgainstSanctionListCreateSerializer(serializers.Serializer):
    file = serializers.FileField(use_url=False, required=True)


class CheckAgainstSanctionListSerializer(serializers.Serializer):
    ok = serializers.BooleanField()
    errors = serializers.ListField(child=serializers.DictField(), required=False)  # type: ignore
