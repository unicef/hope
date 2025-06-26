from rest_framework import serializers

from hct_mis_api.apps.sanction_list.models import (
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

    class Meta:
        model = SanctionListIndividual
        fields = (
            "id",
            "full_name",
            "reference_number",
            "documents",
            "dates_of_birth",
        )


class CheckAgainstSanctionListCreateSerializer(serializers.Serializer):
    file = serializers.FileField(use_url=False, required=True)


class CheckAgainstSanctionListSerializer(serializers.Serializer):
    ok = serializers.BooleanField()
    errors = serializers.ListField(child=serializers.DictField(), required=False)  # type: ignore
