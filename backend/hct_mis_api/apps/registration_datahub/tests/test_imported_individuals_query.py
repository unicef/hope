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
            givenName
            familyName
            phoneNo
            birthDate
          }
        }
      }
    }
    """
    ALL_IMPORTED_INDIVIDUALS_ORDER_BY_BIRTH_DATE_A_QUERY = """
    query AllImportedIndividuals {
      allImportedIndividuals(orderBy: "birth_date") {
        edges {
          node {
            fullName
            givenName
            familyName
            phoneNo
            birthDate
          }
        }
      }
    }
    """
    ALL_IMPORTED_INDIVIDUALS_ORDER_BY_BIRTH_DATE_D_QUERY = """
    query AllImportedIndividuals {
      allImportedIndividuals(orderBy: "-birth_date") {
        edges {
          node {
            fullName
            givenName
            familyName
            phoneNo
            birthDate
          }
        }
      }
    }
    """
    IMPORTED_INDIVIDUAL_QUERY = """
    query ImportedIndividual($id: ID!) {
      importedIndividual(id: $id) {
        fullName
        givenName
        familyName
        phoneNo
        birthDate
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "sex": "MALE",
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
                "sex": "MALE",
            },
            {
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "phone_no": "(548)313-1700-902",
                "birth_date": "1983-12-21",
                "sex": "MALE",
            },
            {
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "phone_no": "(228)231-5473",
                "birth_date": "1973-03-23",
                "sex": "MALE",
            },
            {
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "phone_no": "001-296-358-5428-607",
                "birth_date": "1969-11-29",
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

    def test_imported_individual_query_order_by_dob_a_all(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_IMPORTED_INDIVIDUALS_ORDER_BY_BIRTH_DATE_A_QUERY,
            context={"user": self.user},
        )

    def test_imported_individual_query_order_by_dob_d_all(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_IMPORTED_INDIVIDUALS_ORDER_BY_BIRTH_DATE_D_QUERY,
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
