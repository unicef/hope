from unittest.mock import MagicMock

from django import forms
from django.db import models
import pytest

from extras.test_utils.factories.core import BeneficiaryGroupFactory, DataCollectingTypeFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.household import DocumentFactory, HouseholdFactory
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.payment.fields import DynamicChoiceArrayField, DynamicChoiceField
from hope.apps.payment.services.payment_household_snapshot_service import create_payment_plan_snapshot_data
from hope.models import DataCollectingType, FinancialServiceProviderXlsxTemplate, MergeStatusModel

pytestmark = pytest.mark.django_db


def test_fsp_template_get_column_from_core_field():
    data_collecting_type = DataCollectingTypeFactory(type=DataCollectingType.Type.SOCIAL)
    beneficiary_group = BeneficiaryGroupFactory(name="People", master_detail=False)
    program_cycle = ProgramCycleFactory(
        program=ProgramFactory(data_collecting_type=data_collecting_type, beneficiary_group=beneficiary_group)
    )
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle)
    household = HouseholdFactory(size=1)
    primary = household.head_of_household
    primary.given_name = "John"
    primary.family_name = "Doe"
    primary.middle_name = ""
    primary.full_name = "John Doe"
    primary.phone_no = "+48577123654"
    primary.phone_no_alternative = "+48111222333"
    primary.wallet_name = "wallet_name_Ind_111"
    primary.blockchain_name = "blockchain_name_Ind_111"
    primary.wallet_address = "wallet_address_Ind_111"
    primary.save()

    country = CountryFactory()
    admin_type_1 = AreaTypeFactory(country=country, area_level=1)
    admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
    admin_type_3 = AreaTypeFactory(country=country, area_level=3, parent=admin_type_2)
    area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
    area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
    area3 = AreaFactory(parent=area2, p_code="AF010101", area_type=admin_type_3)
    household.admin1 = area1
    household.admin2 = area2
    household.admin3 = area3
    household.country_origin = country
    household.save()

    payment = PaymentFactory(
        parent=payment_plan,
        household=household,
        collector=primary,
    )

    document = DocumentFactory(
        individual=primary,
        type__key="national_id",
        document_number="id_doc_number_123",
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    admin_areas_dict = FinancialServiceProviderXlsxTemplate.get_areas_dict()
    countries_dict = FinancialServiceProviderXlsxTemplate.get_countries_dict()

    none_resp = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "given_name", admin_areas_dict, countries_dict
    )
    assert none_resp is None

    create_payment_plan_snapshot_data(payment.parent)
    payment.refresh_from_db()

    result = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "invalid_people_field_name", admin_areas_dict, countries_dict
    )
    assert result is None

    given_name = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "given_name", admin_areas_dict, countries_dict
    )
    assert given_name == primary.given_name
    ind_unicef_id = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "individual_unicef_id", admin_areas_dict, countries_dict
    )
    assert ind_unicef_id == primary.unicef_id

    payment.parent.program.data_collecting_type.type = DataCollectingType.Type.STANDARD
    payment.parent.program.data_collecting_type.save()

    size = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "size", admin_areas_dict, countries_dict
    )
    assert size == 1
    admin1 = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "admin1", admin_areas_dict, countries_dict
    )
    assert admin1 == f"{area1.p_code} - {area1.name}"
    admin2 = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "admin2", admin_areas_dict, countries_dict
    )
    assert admin2 == f"{area2.p_code} - {area2.name}"
    admin3 = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "admin3", admin_areas_dict, countries_dict
    )
    assert admin3 == f"{area3.p_code} - {area3.name}"
    given_name = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "given_name", admin_areas_dict, countries_dict
    )
    assert given_name == primary.given_name
    ind_unicef_id = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "individual_unicef_id", admin_areas_dict, countries_dict
    )
    assert ind_unicef_id == primary.unicef_id
    hh_unicef_id = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "household_unicef_id", admin_areas_dict, countries_dict
    )
    assert hh_unicef_id == household.unicef_id
    phone_no = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "phone_no", admin_areas_dict, countries_dict
    )
    assert phone_no == primary.phone_no
    phone_no_alternative = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "phone_no_alternative", admin_areas_dict, countries_dict
    )
    assert phone_no_alternative == primary.phone_no_alternative
    national_id_no = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "national_id_no", admin_areas_dict, countries_dict
    )
    assert national_id_no == document.document_number
    wallet_name = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "wallet_name", admin_areas_dict, countries_dict
    )
    assert wallet_name == primary.wallet_name
    blockchain_name = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "blockchain_name", admin_areas_dict, countries_dict
    )
    assert blockchain_name == primary.blockchain_name
    wallet_address = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "wallet_address", admin_areas_dict, countries_dict
    )
    assert wallet_address == primary.wallet_address

    role = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "role", admin_areas_dict, countries_dict
    )
    assert role == "PRIMARY"

    primary_collector_id = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "primary_collector_id", admin_areas_dict, countries_dict
    )
    assert primary_collector_id == str(primary.pk)

    country_origin = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment, "country_origin", admin_areas_dict, countries_dict
    )
    assert household.country_origin.iso_code3 == country_origin


def test_choices_dynamic_choice_array_field():
    mock_choices = [("field1", "Field 1"), ("field2", "Field 2")]
    mock_choices_callable = MagicMock(return_value=mock_choices)
    field = DynamicChoiceArrayField(
        base_field=models.CharField(max_length=255),
        choices_callable=mock_choices_callable,
    )
    form_field = field.formfield()

    assert list(form_field.choices) == mock_choices
    mock_choices_callable.assert_called_once()
    assert isinstance(form_field, DynamicChoiceField)


def test_model_form_integration_fsp_template():
    class FinancialServiceProviderXlsxTemplateForm(forms.ModelForm):
        class Meta:
            model = FinancialServiceProviderXlsxTemplate
            fields = ["core_fields"]

    form = FinancialServiceProviderXlsxTemplateForm(data={"core_fields": ["age", "residence_status"]})
    assert form.is_valid()
    template = form.save()
    assert template.core_fields == ["age", "residence_status"]

    form = FinancialServiceProviderXlsxTemplateForm(data={"core_fields": ["field1"]})
    assert not form.is_valid()
    assert form.errors == {"core_fields": ["Select a valid choice. field1 is not one of the available choices."]}
