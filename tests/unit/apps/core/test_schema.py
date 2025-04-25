from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    DataCollectingTypeFactory,
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
)
from hct_mis_api.apps.core.models import (
    DataCollectingType,
    FlexibleAttribute,
    PeriodicFieldData,
)
from hct_mis_api.apps.core.utils import encode_id_base64_required
from hct_mis_api.apps.payment.fixtures import generate_delivery_mechanisms
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestDataCollectionTypeSchema(APITestCase):
    QUERY_DATA_COLLECTING_TYPE_CHOICES = """
        query dataCollectionTypeChoiceData {
            dataCollectionTypeChoices {
              name
              value
              type
            }
        }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()

        cls.data_collecting_type_full = DataCollectingTypeFactory(
            label="Full", code="full", weight=1, business_areas=[cls.business_area]
        )
        cls.data_collecting_type_partial = DataCollectingTypeFactory(
            label="Partial",
            code="partial",
            weight=2,
            business_areas=[cls.business_area],
            type=DataCollectingType.Type.SOCIAL,
        )
        cls.data_collecting_type_size_only = DataCollectingTypeFactory(
            label="Size Only", code="size_only", weight=3, business_areas=[cls.business_area]
        )
        cls.data_collecting_type_unknown = DataCollectingTypeFactory(
            label="Unknown", code="unknown", weight=4, business_areas=[cls.business_area]
        )

    def test_dct_with_unknown_code_is_not_in_list(self) -> None:  # also checks weight sorting
        self.snapshot_graphql_request(
            request_string=self.QUERY_DATA_COLLECTING_TYPE_CHOICES,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
        )


class TestPDUSubtypeChoices(APITestCase):
    QUERY_PDU_SUBTYPE_CHOICES = """
        query pduSubtypeChoicesData {
            pduSubtypeChoices {
              value
              displayName
            }
        }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()

    def test_pdu_subtype_choices_data(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_PDU_SUBTYPE_CHOICES,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
        )


class TestAllPduFields(APITestCase):
    QUERY_ALL_PUD_FIELDS = """
        query allPduFields ($businessAreaSlug: String!, $programId: String!) {
            allPduFields (businessAreaSlug: $businessAreaSlug, programId: $programId) {
              type
              name
              labelEn
              pduData {
                subtype
                numberOfRounds
                roundsNames
              }
            }
        }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(
            business_area=cls.business_area, status=Program.ACTIVE, name="Test Program For PDU Fields"
        )
        cls.user = UserFactory()

        pdu_data1 = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=3,
            rounds_names=["Round 1", "Round 2", "Round 3"],
        )
        FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field 1",
            pdu_data=pdu_data1,
        )
        pdu_data2 = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=2,
            rounds_names=["Round 1", "Round 2"],
        )
        FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field 2",
            pdu_data=pdu_data2,
        )

        # Create a PDU field for a different program
        other_program = ProgramFactory(business_area=cls.business_area, status=Program.ACTIVE, name="Other Program")
        pdu_data_different_program = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.BOOL,
            number_of_rounds=1,
            rounds_names=["Round 1"],
        )
        FlexibleAttributeForPDUFactory(
            program=other_program,
            label="PDU Field Different Program",
            pdu_data=pdu_data_different_program,
        )
        # Create a non-PDU field
        FlexibleAttribute.objects.create(
            type=FlexibleAttribute.STRING,
            label={"English(EN)": "value", "Not PDU Field": ""},
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        )

    def test_pdu_subtype_choices_data(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_ALL_PUD_FIELDS,
            variables={
                "businessAreaSlug": "afghanistan",
                "programId": encode_id_base64_required(self.program.id, "Program"),
            },
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
        )


class TestAllCollectorsFields(APITestCase):
    QUERY_ALL_COLLECTORS_FIELDS = """
        query CollFields {
          allCollectorFieldsAttributes {
            name
            labelEn
          }
        }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()
        generate_delivery_mechanisms()

    def test_collectors_fields_choices_data(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_ALL_COLLECTORS_FIELDS,
            variables={
                "businessAreaSlug": "afghanistan",
            },
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
        )
