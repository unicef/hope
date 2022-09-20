from django.utils import timezone
from django.utils.functional import cached_property

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import (
    HEAD,
    RELATIONSHIP_CHOICE,
    ROLE_CHOICE,
    Household,
    Individual,
)

DETAILS_POLICY = (
    ["NO", "NO"],
    ["FULL", "FULL"],
    ["PARTIAL", "PARTIAL"],
)


class IndividualSerializer(serializers.ModelSerializer):
    first_registration_date = serializers.DateTimeField(default=timezone.now)
    last_registration_date = serializers.DateTimeField(default=timezone.now)

    # relationship = serializers.ChoiceField(choices=([None, ""],) + RELATIONSHIP_CHOICE)
    # role = serializers.ChoiceField(choices=ROLE_CHOICE)

    class Meta:
        model = Individual
        exclude = [
            "business_area",
        ]


class HouseholdSerializer(serializers.ModelSerializer):
    first_registration_date = serializers.DateTimeField(default=timezone.now)
    last_registration_date = serializers.DateTimeField(default=timezone.now)
    members = IndividualSerializer(many=True)
    collect_individual_data = serializers.ChoiceField(choices=DETAILS_POLICY)

    class Meta:
        model = Household
        exclude = ["id", "head_of_household", "business_area"]

    def __init__(self, *args, **kwargs):
        self.business_area = kwargs.pop("business_area")
        super().__init__(*args, **kwargs)

    def validate_collect_individual_data(self, attrs):
        return ""

    def validate(self, attrs):
        hh = list(filter(lambda m: m["relationship"] == HEAD, attrs["members"]))
        if len(hh) == 1:
            attrs["head_of_household"] = hh[0]
        elif len(hh) > 1:
            raise ValidationError("Multiple Head Of Household")
        else:
            raise ValidationError("Missing Head Of Household")
        return super().validate(attrs)

    def create(self, validated_data):
        members = validated_data.pop("members")
        hoh = Individual.objects.create(**validated_data.pop("head_of_household"), business_area=self.business_area)

        household = Household.objects.create(
            business_area=self.business_area, head_of_household=hoh, **validated_data
        )  # create the master reservation object
        for member in members:
            # create a details_reservation referencing the master reservation
            Individual.objects.create(**member, business_area=self.business_area, household=household)
        return household


class UploadRDIView(APIView):
    @cached_property
    def selected_business_area(self):
        return BusinessArea.objects.get(slug=self.kwargs["business_area"])

    def post(self, request, business_area):
        serializer = HouseholdSerializer(data=request.data, business_area=self.selected_business_area)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "unicef_id": serializer.instance.unicef_id,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
