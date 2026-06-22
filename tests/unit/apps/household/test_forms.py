from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import modelform_factory
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DataCollectingTypeFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentPlanGroupFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    XlsxUpdateFileFactory,
)
from hope.apps.household.forms import (
    CreateTargetPopulationTextForm,
    DocumentForm,
    IndividualForm,
    MassEnrollForm,
    UpdateByXlsxStage1Form,
    UpdateByXlsxStage2Form,
    WithdrawHouseholdsForm,
    get_households_from_text,
)
from hope.models import BusinessArea, Household, Individual, PendingDocument, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def data_collecting_type(business_area):
    dct = DataCollectingTypeFactory()
    dct.limit_to.add(business_area)
    return dct


@pytest.fixture
def program(business_area, data_collecting_type) -> Program:
    return ProgramFactory(
        name="Test Program 333",
        business_area=business_area,
        status=Program.ACTIVE,
        data_collecting_type=data_collecting_type,
    )


@pytest.fixture
def household(program) -> Household:
    return HouseholdFactory(
        program=program,
        business_area=program.business_area,
        head_of_household=IndividualFactory(household=None),
    )


def _stage1_file() -> SimpleUploadedFile:
    return SimpleUploadedFile("update.xlsx", b"content")


class TestMassEnrollForm:
    def test_clean_form(self, business_area, program, household) -> None:
        form_data = {"program_for_enroll": program.id, "apply": True}
        form = MassEnrollForm(
            data=form_data,
            business_area_id=str(business_area.id),
            households=Household.objects.filter(id=household.id),
        )
        assert form.is_valid()

    def test_warns_on_incompatible_data_collecting_type(self, business_area, program, household) -> None:
        other_program = ProgramFactory(
            business_area=business_area,
            status=Program.ACTIVE,
            beneficiary_group=program.beneficiary_group,
            data_collecting_type=DataCollectingTypeFactory(),
        )

        form = MassEnrollForm(
            data={"program_for_enroll": other_program.id, "apply": True},
            business_area_id=str(business_area.id),
            households=Household.objects.filter(id=household.id),
        )

        assert not form.is_valid()
        assert any("compatible" in str(e) for e in form.non_field_errors())

    def test_errors_on_different_beneficiary_group(self, business_area, program, household) -> None:
        program.data_collecting_type.compatible_types.add(program.data_collecting_type)
        other_program = ProgramFactory(
            business_area=business_area,
            status=Program.ACTIVE,
            data_collecting_type=program.data_collecting_type,
        )

        form = MassEnrollForm(
            data={"program_for_enroll": other_program.id, "apply": True},
            business_area_id=str(business_area.id),
            households=Household.objects.filter(id=household.id),
        )

        assert not form.is_valid()
        assert any("beneficiary group" in str(e) for e in form.non_field_errors())

    def test_skips_validation_without_apply(self, business_area, program, household) -> None:
        form = MassEnrollForm(
            data={"program_for_enroll": program.id},
            business_area_id=str(business_area.id),
            households=Household.objects.filter(id=household.id),
        )

        assert form.is_valid()


class TestGetHouseholdsFromText:
    def test_unicef_id_space_separator(self, program, household) -> None:
        result = get_households_from_text(program, household.unicef_id, "unicef_id", "space")

        assert household in result

    def test_unicef_id_new_line_separator(self, program, household) -> None:
        result = get_households_from_text(program, household.unicef_id, "unicef_id", "new_line")

        assert household in result

    def test_unique_id_target_field(self, program, household) -> None:
        result = get_households_from_text(program, str(household.id), "unique_id", ",")

        assert household in result

    def test_unknown_target_field_returns_empty_list(self, program, household) -> None:
        result = get_households_from_text(program, household.unicef_id, "something_else", ",")

        assert result == []


class TestCreateTargetPopulationTextForm:
    def test_requires_program(self) -> None:
        with pytest.raises(forms.ValidationError):
            CreateTargetPopulationTextForm(program=None)

    def test_read_only_hides_widgets(self, program) -> None:
        form = CreateTargetPopulationTextForm(program=program, read_only=True)

        assert isinstance(form.fields["name"].widget, forms.HiddenInput)
        assert isinstance(form.fields["criteria"].widget, forms.HiddenInput)
        assert isinstance(form.fields["program_cycle"].widget, forms.HiddenInput)

    def test_clean_criteria_returns_households(self, program, household) -> None:
        cycle = program.cycles.first()
        payment_plan_group = PaymentPlanGroupFactory(cycle=cycle)
        form = CreateTargetPopulationTextForm(
            data={
                "action": "create",
                "name": "TP",
                "target_field": "unicef_id",
                "separator": ",",
                "criteria": household.unicef_id,
                "program_cycle": cycle.pk,
                "payment_plan_group": payment_plan_group.pk,
            },
            program=program,
        )

        assert form.is_valid()
        assert household in form.cleaned_data["criteria"]

    def test_clean_criteria_raises_on_missing_field(self, program) -> None:
        form = CreateTargetPopulationTextForm(
            data={
                "action": "create",
                "name": "TP",
                "separator": ",",
                "criteria": "any-id",
            },
            program=program,
        )

        assert not form.is_valid()
        assert "criteria" in form.errors


class TestWithdrawHouseholdsForm:
    def test_filters_program_queryset_by_business_area(self, business_area, program) -> None:
        form = WithdrawHouseholdsForm(business_area=business_area)

        assert program in form.fields["program"].queryset

    def test_without_business_area_has_empty_program_queryset(self) -> None:
        form = WithdrawHouseholdsForm()

        assert list(form.fields["program"].queryset) == []


class TestIndividualForm:
    def test_overrides_household_queryset(self) -> None:
        pending_household = PendingHouseholdFactory()
        form_class = modelform_factory(Individual, form=IndividualForm, fields=["household"])

        form = form_class(data={"household": pending_household})

        assert form.fields["household"].queryset.model.__name__ == "PendingHousehold"

    def test_without_relation_fields_builds(self) -> None:
        form_class = modelform_factory(Individual, form=IndividualForm, fields=["full_name"])

        form = form_class(data={"full_name": "Jane Doe"})

        assert "individual" not in form.fields
        assert "household" not in form.fields


class TestDocumentForm:
    def test_overrides_individual_queryset(self) -> None:
        pending_individual = PendingIndividualFactory(household=None)
        document_type = DocumentTypeFactory(key="national_id")
        form_class = modelform_factory(PendingDocument, form=DocumentForm, fields=["individual", "type"])

        form = form_class(data={"individual": pending_individual, "type": document_type})

        assert form.fields["individual"].queryset.model.__name__ == "PendingIndividual"

    def test_without_individual_field_builds(self) -> None:
        document_type = DocumentTypeFactory(key="passport")
        form_class = modelform_factory(PendingDocument, form=DocumentForm, fields=["type"])

        form = form_class(data={"type": document_type})

        assert "individual" not in form.fields


class TestUpdateByXlsxStage1Form:
    def test_valid(self, business_area, program) -> None:
        rdi = RegistrationDataImportFactory(business_area=business_area, program=program, name="RDI-1")

        form = UpdateByXlsxStage1Form(
            data={
                "business_area": business_area.pk,
                "program": program.pk,
                "registration_data_import": rdi.pk,
            },
            files={"file": _stage1_file()},
        )

        assert form.is_valid()
        assert form.cleaned_data["registration_data_import"] == rdi

    def test_program_must_match_business_area(self, business_area, program) -> None:
        other_business_area = BusinessAreaFactory(slug="ukraine", name="Ukraine")

        form = UpdateByXlsxStage1Form(
            data={
                "business_area": other_business_area.pk,
                "program": program.pk,
                "registration_data_import": "",
            },
            files={"file": _stage1_file()},
        )

        assert not form.is_valid()
        assert "Program should belong to selected business area." in form.errors["program"]

    def test_rdi_must_match_business_area(self, business_area, program) -> None:
        other_business_area = BusinessAreaFactory(slug="ukraine", name="Ukraine")
        rdi = RegistrationDataImportFactory(business_area=other_business_area, program=program, name="RDI-2")

        form = UpdateByXlsxStage1Form(
            data={
                "business_area": business_area.pk,
                "program": program.pk,
                "registration_data_import": rdi.pk,
            },
            files={"file": _stage1_file()},
        )

        assert not form.is_valid()
        assert any("business area" in str(e) for e in form.errors["registration_data_import"])

    def test_rdi_must_match_program(self, business_area, program) -> None:
        other_program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
        rdi = RegistrationDataImportFactory(business_area=business_area, program=other_program, name="RDI-3")

        form = UpdateByXlsxStage1Form(
            data={
                "business_area": business_area.pk,
                "program": program.pk,
                "registration_data_import": rdi.pk,
            },
            files={"file": _stage1_file()},
        )

        assert not form.is_valid()
        assert any("Program" in str(e) for e in form.errors["registration_data_import"])


class TestUpdateByXlsxStage2Form:
    def test_valid_with_required_columns(self, business_area) -> None:
        xlsx_file = XlsxUpdateFileFactory(business_area=business_area)
        columns = ["individual__unicef_id", "household__unicef_id", "extra"]

        form = UpdateByXlsxStage2Form(
            data={
                "xlsx_update_file": xlsx_file.pk,
                "xlsx_match_columns": ["individual__unicef_id", "household__unicef_id"],
            },
            xlsx_columns=columns,
        )

        assert form.is_valid()

    def test_requires_unicef_id_columns(self, business_area) -> None:
        xlsx_file = XlsxUpdateFileFactory(business_area=business_area)
        columns = ["individual__unicef_id", "household__unicef_id", "extra"]

        form = UpdateByXlsxStage2Form(
            data={
                "xlsx_update_file": xlsx_file.pk,
                "xlsx_match_columns": ["extra"],
            },
            xlsx_columns=columns,
        )

        assert not form.is_valid()
        assert "Unicef Id columns have to be selected" in str(form.errors["xlsx_match_columns"])
