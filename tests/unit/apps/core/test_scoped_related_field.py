"""ScopedRelatedField narrows a related field to the scope the view puts in the context (GHSA-2xf8-jjc2-9pmv)."""

import pytest
from rest_framework import serializers

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory
from hope.apps.core.api.fields import ScopedRelatedField, ScopedSlugRelatedField
from hope.models import BusinessArea, Program

pytestmark = pytest.mark.django_db


class ProgramInputSerializer(serializers.Serializer):
    program = ScopedRelatedField(queryset=Program.objects.all())


class ProgramByCodeInputSerializer(serializers.Serializer):
    program = ScopedSlugRelatedField(queryset=Program.objects.all(), slug_field="code", scope="business_area")


class ProgramCustomPathInputSerializer(serializers.Serializer):
    program = ScopedRelatedField(
        queryset=Program.objects.all(), scope="business_area", scope_path="business_area__slug"
    )


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def own_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, code="OWN1")


@pytest.fixture
def foreign_program() -> Program:
    return ProgramFactory(business_area=BusinessAreaFactory(name="Ukraine", slug="ukraine"), code="FRGN")


def test_id_inside_the_scope_resolves(business_area: BusinessArea, own_program: Program) -> None:
    serializer = ProgramInputSerializer(data={"program": own_program.id}, context={"business_area": business_area})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["program"] == own_program


def test_id_outside_the_scope_fails_like_a_missing_id(business_area: BusinessArea, foreign_program: Program) -> None:
    serializer = ProgramInputSerializer(data={"program": foreign_program.id}, context={"business_area": business_area})

    assert not serializer.is_valid()
    assert "does not exist" in str(serializer.errors["program"][0])


def test_slug_inside_the_scope_resolves(business_area: BusinessArea, own_program: Program) -> None:
    serializer = ProgramByCodeInputSerializer(data={"program": "OWN1"}, context={"business_area": business_area})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["program"] == own_program


def test_slug_outside_the_scope_fails_like_a_missing_slug(
    business_area: BusinessArea, foreign_program: Program
) -> None:
    serializer = ProgramByCodeInputSerializer(data={"program": "FRGN"}, context={"business_area": business_area})

    assert not serializer.is_valid()
    assert "does not exist" in str(serializer.errors["program"][0])


def test_scope_path_walks_the_named_relation(business_area: BusinessArea, own_program: Program) -> None:
    serializer = ProgramCustomPathInputSerializer(
        data={"program": own_program.id}, context={"business_area": business_area.slug}
    )

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["program"] == own_program


def test_scope_missing_from_the_context_names_the_culprit(own_program: Program) -> None:
    serializer = ProgramInputSerializer(data={"program": own_program.id}, context={})

    with pytest.raises(KeyError, match="'business_area' is missing from the serializer context"):
        serializer.is_valid()
