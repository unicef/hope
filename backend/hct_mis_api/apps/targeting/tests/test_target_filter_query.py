import datetime as dt
import json

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import LocationFactory
from household.fixtures import HouseholdFactory
from household.fixtures import IndividualFactory
from registration_data.fixtures import RegistrationDataImportFactory


class TestTargetFilterQuery(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        intake_group = "some group name"
        argument_payload = [
            {
                "intake_group": intake_group,
                "sex": "M",
                "age_min": 1,
                "age_max": 39,
                # "school_distance_min": 1,
                # "school_distance_min": 10,
                "num_individuals_min": 2,
                "num_individuals_max": 6,
            },
            {
                "intake_group": intake_group,
                "sex": "F",
                "age_min": 10,
                "age_max": 31,
                # "school_distance_min": 1,
                # "school_distance_min": 10,
                "num_individuals_min": 2,
                "num_individuals_max": 6,
            },
        ]
        cls.serialized_payload = json.dumps(argument_payload)
        cls.location = LocationFactory.create(title="some town")
        cls.registration_import_data = RegistrationDataImportFactory.create(
            name=intake_group)
        cls.head_of_household_1 = IndividualFactory.create(
            full_name="John Doe",
            first_name="John",
            last_name="Doe",
            sex="Male",
            dob=dt.date(2000, 3, 3))
        cls.head_of_household_2 = IndividualFactory.create(
            full_name="Jane Doe",
            first_name="Jane",
            last_name="Doe",
            sex="Female",
            dob=dt.date(1996, 3, 3))
        filters_to_create = [
            {
                "household_ca_id": "ca_id_1",
                "head_of_household": cls.head_of_household_1,
                "family_size": 5,
                "address": "some street",
                "location": cls.location,
                "registration_data_import_id": cls.registration_import_data,
            },
            {
                "household_ca_id": "ca_id_2",
                "head_of_household": cls.head_of_household_2,
                "family_size": 5,
                "address": "sample street",
                "location": cls.location,
                "registration_data_import_id": cls.registration_import_data,
            },
        ]
        cls.filter_entries = [
            # This is mocked HouseHold Model.
            HouseholdFactory(**data) for data in filters_to_create
        ]
        # graph query to be called.
        cls.FILTER_QUERY = """
                query targetFilters($serializedList: String!) {
                    targetFilters(serializedList: $serializedList) {
                        householdCaId
                        headOfHousehold {
                            fullName
                            firstName
                            lastName
                            dob
                        }
                        familySize
                        address
                        location {
                            title
                        }
                        registrationDataImportId {
                            name
                        }
                    }
                }
                """

    def test_filter_query(self):
        self.snapshot_graphql_request(
            request_string=self.FILTER_QUERY,
            context={"user": self.user},
            variables={
                "serializedList": self.serialized_payload,
                # base64.b64encode(
                #     f"{self.serialized_payload}".encode("utf-8")).decode()
            },
        )
