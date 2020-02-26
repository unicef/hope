from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from registration_datahub.fixtures import ImportedIndividualFactory


class TestImportedIndividualQuery(APITestCase):
    multi_db = True

    # IMPORTANT!
    # FREEZGUN doesn't work this snapshot have to be updated once a year
    MAX_AGE = 51
    MIN_AGE = 37

    ALL_IMPORTED_INDIVIDUALS_QUERY = """
    query AllImportedIndividuals {
      allImportedIndividuals {
        edges {
          node {
            fullName
            firstName
            lastName
            phoneNumber
            dob
          }
        }
      }
    }
    """
    ALL_IMPORTED_INDIVIDUALS_AGE_RANGE = f"""
    query AllImportedIndividuals {{
      allImportedIndividuals(
        age: "{{\\"min\\": {MIN_AGE}, \\"max\\": {MAX_AGE}}}"
      ) {{
        edges {{
          node {{
            fullName
            firstName
            lastName
            phoneNumber
            dob
          }}
        }}
      }}
    }}
    """
    ALL_IMPORTED_INDIVIDUALS_AGE_MIN = f"""
    query AllImportedIndividuals {{
      allImportedIndividuals(
        age: "{{\\"min\\": {MIN_AGE}}}"
      ) {{
        edges {{
          node {{
            fullName
            firstName
            lastName
            phoneNumber
            dob
          }}
        }}
      }}
    }}
    """
    ALL_IMPORTED_INDIVIDUALS_AGE_MAX = f"""
    query AllImportedIndividuals {{
      allImportedIndividuals(
        age: "{{\\"max\\": {MAX_AGE}}}"
      ) {{
        edges {{
          node {{
            fullName
            firstName
            lastName
            phoneNumber
            dob
          }}
        }}
      }}
    }}
    """
    ALL_IMPORTED_INDIVIDUALS_SEX = """
    query AllImportedIndividuals {
      allImportedIndividuals(sex: "FEMALE") {
        edges {
          node {
            fullName
            firstName
            lastName
            phoneNumber
            dob
          }
        }
      }
    }
    """
    IMPORTED_INDIVIDUAL_QUERY = """
    query ImportedIndividual($id: ID!) {
      importedIndividual(id: $id) {
        fullName
        firstName
        lastName
        phoneNumber
        dob
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "first_name": "Benjamin",
                "last_name": "Butler",
                "phone_number": "(953)682-4596",
                "dob": "1943-07-30",
                "sex": "MALE",
            },
            {
                "full_name": "Robin Ford",
                "first_name": "Robin",
                "last_name": "Ford",
                "phone_number": "+18663567905",
                "dob": "1946-02-15",
                "sex": "MALE",
            },
            {
                "full_name": "Timothy Perry",
                "first_name": "Timothy",
                "last_name": "Perry",
                "phone_number": "(548)313-1700-902",
                "dob": "1983-12-21",
                "sex": "MALE",
            },
            {
                "full_name": "Eric Torres",
                "first_name": "Eric",
                "last_name": "Torres",
                "phone_number": "(228)231-5473",
                "dob": "1973-03-23",
                "sex": "MALE",
            },
            {
                "full_name": "Jenna Franklin",
                "first_name": "Jenna",
                "last_name": "Franklin",
                "phone_number": "001-296-358-5428-607",
                "dob": "1969-11-29",
                "sex": "FEMALE",
            },
        ]

        self.individuals = [
            ImportedIndividualFactory(**individual)
            for individual in self.individuals_to_create
        ]

    def test_imported_individual_query_all(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_IMPORTED_INDIVIDUALS_QUERY,
            context={"user": self.user},
        )

    def test_imported_individual_query_age_range(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_IMPORTED_INDIVIDUALS_AGE_RANGE,
            context={"user": self.user},
        )

    def test_imported_individual_query_age_min(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_IMPORTED_INDIVIDUALS_AGE_MIN,
            context={"user": self.user},
        )

    def test_imported_individual_query_age_max(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_IMPORTED_INDIVIDUALS_AGE_MAX,
            context={"user": self.user},
        )

    def test_imported_individual_query_sex(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_IMPORTED_INDIVIDUALS_SEX,
            context={"user": self.user},
        )

    def test_imported_individual_query_single(self):
        self.snapshot_graphql_request(
            request_string=self.IMPORTED_INDIVIDUAL_QUERY,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.individuals[0].id, "ImportedIndividual",
                )
            },
        )
