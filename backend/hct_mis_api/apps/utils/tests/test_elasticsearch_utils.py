from hct_mis_api.apps.account.permissions import Permissions


class TestIndividualQuery(BaseElasticSearchTestCase, APITestCase):
    databases = {"default", "registration_datahub"}

    ALL_INDIVIDUALS_QUERY = """
    query AllIndividuals($search: String) {
      allIndividuals(businessArea: "afghanistan", search: $search, orderBy:"id") {
        edges {
          node {
            fullName
            givenName
            familyName
            phoneNo
            phoneNoValid
            birthDate
          }
        }
      }
    }
    """

    ALL_INDIVIDUALS_BY_PROGRAMME_QUERY = """
    query AllIndividuals($programs: [ID]) {
      allIndividuals(programs: $programs, orderBy: "birth_date", businessArea: "afghanistan") {
        edges {
          node {
            givenName
            familyName
            phoneNo
            birthDate
            household {
              programs {
                edges {
                  node {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    INDIVIDUAL_QUERY = """
    query Individual($id: ID!) {
      individual(id: $id, orderBy:"id") {
        fullName
        givenName
        familyName
        phoneNo
        birthDate
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.business_area = create_afghanistan()
        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=cls.business_area,
            status=Program.ACTIVE,
        )
        cls.program_two = ProgramFactory(
            name="Test program TWO",
            business_area=cls.business_area,
            status=Program.ACTIVE,
        )

        cls.household_one = HouseholdFactory.build(business_area=cls.business_area)
        cls.household_two = HouseholdFactory.build(business_area=cls.business_area)
        cls.household_one.registration_data_import.imported_by.save()
        cls.household_one.registration_data_import.save()
        cls.household_two.registration_data_import.imported_by.save()
        cls.household_two.registration_data_import.save()
        cls.household_one.programs.add(program_one)
        cls.household_two.programs.add(cls.program_two)
        # added for testing migrate_data_to_representations script
        cls.household_two.programs.add(program_one)

        cls.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "id": "ffb2576b-126f-42de-b0f5-ef889b7bc1fe",
                "registration_id": 1,
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
                "id": "8ef39244-2884-459b-ad14-8d63a6fe4a4a",
            },
            {
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "phone_no": "(548)313-1700-902",
                "birth_date": "1983-12-21",
                "id": "badd2d2d-7ea0-46f1-bb7a-69f385bacdcd",
            },
            {
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "phone_no": "(228)231-5473",
                "birth_date": "1973-03-23",
                "id": "2c1a26a3-2827-4a99-9000-a88091bf017c",
            },
            {
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "phone_no": "001-296-358-5428-607",
                "birth_date": "1969-11-29",
                "id": "0fc995cc-ea72-4319-9bfe-9c9fda3ec191",
            },
            {
                "full_name": "James Bond",
                "given_name": "James",
                "family_name": "Bond",
                "phone_no": "(007)682-4596",
                "birth_date": "1965-06-26",
                "id": "972fdac5-d1bf-44ed-a4a5-14805b5dc606",
            },
            {
                "full_name": "Peter Parker",
                "given_name": "Peter",
                "family_name": "Parker",
                "phone_no": "(666)682-2345",
                "birth_date": "1978-01-02",
                "id": "430924a6-273e-4018-95e7-b133afa5e1b9",
            },
        ]

        cls.individuals = [
            IndividualFactory(household=cls.household_one if index % 2 else cls.household_two, **individual)
            for index, individual in enumerate(cls.individuals_to_create)
        ]
        cls.household_one.head_of_household = cls.individuals[0]
        cls.household_two.head_of_household = cls.individuals[1]
        cls.household_one.save()
        cls.household_two.save()

        cls.bank_account_info = BankAccountInfoFactory(
            individual=cls.individuals[5], bank_name="ING", bank_account_number=11110000222255558888999925
        )

        cls.individual_unicef_id_to_search = Individual.objects.get(full_name="Benjamin Butler").unicef_id
        cls.household_unicef_id_to_search = Individual.objects.get(full_name="Benjamin Butler").household.unicef_id

        DocumentTypeFactory(key="national_id")
        DocumentTypeFactory(key="national_passport")
        DocumentTypeFactory(key="tax_id")
        DocumentTypeFactory(key="birth_certificate")
        DocumentTypeFactory(key="disability_card")
        DocumentTypeFactory(key="drivers_license")

        cls.national_id = DocumentFactory(
            document_number="123-456-789",
            type=DocumentType.objects.get(key="national_id"),
            individual=cls.individuals[0],
        )

        cls.national_passport = DocumentFactory(
            document_number="111-222-333",
            type=DocumentType.objects.get(key="national_passport"),
            individual=cls.individuals[1],
        )

        cls.tax_id = DocumentFactory(
            document_number="666-777-888", type=DocumentType.objects.get(key="tax_id"), individual=cls.individuals[2]
        )

        cls.birth_certificate = DocumentFactory(
            document_number="111222333",
            type=DocumentType.objects.get(key="birth_certificate"),
            individual=cls.individuals[4],
        )

        cls.disability_card = DocumentFactory(
            document_number="10000000000",
            type=DocumentType.objects.get(key="disability_card"),
            individual=cls.individuals[6],
        )

        cls.drivers_license = DocumentFactory(
            document_number="1234567890",
            type=DocumentType.objects.get(key="drivers_license"),
            individual=cls.individuals[0],
        )

        cls.rebuild_search_index()

        # remove after data migration
        migrate_data_to_representations()

        super().setUpTestData()

    def test_query_individuals_by_search_drivers_license_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        # Should be Benjamin Butler
        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={"user": self.user},
            variables={"search": f"drivers_license {self.drivers_license.document_number}"},
        )