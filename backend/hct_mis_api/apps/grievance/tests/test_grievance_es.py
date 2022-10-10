import json
import os
from unittest.mock import patch

from django.core.management import call_command
from elasticsearch import Elasticsearch

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.constants import (
    PRIORITY_LOW,
    PRIORITY_HIGH,
    URGENCY_URGENT,
    URGENCY_VERY_URGENT,
)


def execute_test_es_query(query_dict):
    es = Elasticsearch("http://elasticsearch:9200")
    es.indices.refresh("test_es_db")

    resp = es.search(index="test_es_db", body=query_dict)
    es_ids = []
    for hit in resp["hits"]["hits"]:
        es_ids.append(hit["_id"])

    es.indices.refresh("test_es_db")
    return es_ids


@patch("hct_mis_api.apps.core.es_filters.ElasticSearchFilterSet.USE_ALL_FIELDS_AS_POSTGRES_DB", False)
class TestGrievanceQueryElasticSearch(APITestCase):
    PERMISSION = (
        Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
        Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
        Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
        Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
        Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
        Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
    )

    FILTER_BY_SEARCH = """
        query AllGrievanceTickets($search: String) {
          allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", search: $search) {
            edges {
              node {
                householdUnicefId
                category
                status
                issueType
                language
                description
                consent
                urgency
                priority
              }
            }
          }
        }
    """

    FILTER_BY_ADMIN_AREA = """
    query AllGrievanceTickets($admin: [ID]) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", admin: $admin) {
        edges {
          node {
            householdUnicefId
            category
            status
            issueType
            language
            description
            consent
            urgency
            priority
          }
        }
      }
    }
    """

    FILTER_BY_CREATED_AT = """
    query AllGrievanceTickets($createdAtRange: String) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", createdAtRange: $createdAtRange) {
        edges {
          node {
            householdUnicefId
            category
            status
            issueType
            language
            description
            consent
            urgency
            priority
          }
        }
      }
    }
    """

    FILTER_BY_STATUS = """
    query AllGrievanceTickets($status: [String]) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", status: $status) {
        edges {
          node {
            householdUnicefId
            category
            status
            issueType
            language
            description
            consent
            urgency
            priority
          }
        }
      }
    }
    """

    FILTER_BY_CATEGORY = """
    query AllGrievanceTickets($category: String) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", category: $category) {
        edges {
          node {
            householdUnicefId
            category
            status
            issueType
            language
            description
            consent
            urgency
            priority
          }
        }
      }
    }
    """

    FILTER_BY_ASSIGNED_TO = """
    query AllGrievanceTickets($assignedTo: ID) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", assignedTo: $assignedTo) {
        edges {
          node {
            householdUnicefId
            category
            status
            issueType
            language
            description
            consent
            urgency
            priority
          }
        }
      }
    }
    """

    FILTER_BY_ISSUE_TYPE = """
        query AllGrievanceTickets($issueType: String) {
          allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", issueType: $issueType) {
            edges {
              node {
                householdUnicefId
                category
                status
                issueType
                language
                description
                consent
                urgency
                priority
              }
            }
          }
        }
        """

    FILTER_BY_PRIORITY = """
        query AllGrievanceTickets($priority: String) {
          allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", priority: $priority) {
            edges {
              node {
                householdUnicefId
                category
                status
                issueType
                language
                description
                consent
                urgency
                priority
              }
            }
          }
        }
        """

    FILTER_BY_URGENCY = """
    query AllGrievanceTickets($urgency: String) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", urgency: $urgency) {
        edges {
          node {
            householdUnicefId
            category
            status
            issueType
            language
            description
            consent
            urgency
            priority
          }
        }
      }
    }
    """

    FILTER_BY_REGISTRATION_DATA_IMPORT = """
    query AllGrievanceTickets($registrationDataImport: ID) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", registrationDataImport: $registrationDataImport) {
        edges {
          node {
            householdUnicefId
            category
            status
            issueType
            language
            description
            consent
            urgency
            priority
          }
        }
      }
    }
    """

    FILTER_BY_GRIEVANCE_TYPE = """
        query AllGrievanceTickets($grievanceType: String) {
          allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", grievanceType: $grievanceType) {
            edges {
              node {
                householdUnicefId
                category
                status
                issueType
                language
                description
                consent
                urgency
                priority
              }
            }
          }
        }
        """

    FILTER_BY_MULTIPLE_FILTERS = """
        query AllGrievanceTickets(
          $status: [String], 
          $priority: String, 
          $urgency: String, 
          $grievanceType: String
        ) {
          allGrievanceTicket(
            businessArea: "afghanistan", 
            orderBy: "created_at", 
            status: $status,
            priority: $priority,
            urgency: $urgency,
            grievanceType: $grievanceType
          ) {
            edges {
              node {
                householdUnicefId
                category
                status
                issueType
                language
                description
                consent
                urgency
                priority
              }
            }
          }
        }
    """

    @classmethod
    def setUpTestData(cls):
        cls.es = cls.create_es_db()

        create_afghanistan()
        call_command("loadcountries")

        cls.user = UserFactory.create()
        cls.user2 = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        country = Country.objects.first()
        area_type_new = AreaTypeFactory(
            name="Admin type one",
            area_level=2,
            country=country,
        )
        cls.admin_area_1 = AreaFactory(name="City Test", area_type=area_type_new, p_code="123aa123")
        cls.admin_area_2 = AreaFactory(name="City Example", area_type=area_type_new, p_code="sadasdasfd222")

        cls.grievance_ticket_1 = GrievanceTicket.objects.create(
            **{
                "business_area": cls.business_area,
                "unicef_id": "GRV-0000001",
                "admin2": cls.admin_area_1,
                "language": "Polish",
                "consent": True,
                "description": "grievance_ticket_1",
                "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                "status": GrievanceTicket.STATUS_NEW,
                "created_by": cls.user,
                "assigned_to": cls.user,
                "created_at": "2022-04-30T09:54:07.827000",
                "household_unicef_id": "HH-20-0000.0001",
                "priority": 1,
                "urgency": 2,
            }
        )

        cls.es.index(
            index="test_es_db",
            doc_type="_doc",
            id=cls.grievance_ticket_1.id,
            body={
                "business_area": {"slug": cls.grievance_ticket_1.business_area.name.lower()},
                "unicef_id": cls.grievance_ticket_1.unicef_id,
                "admin2": {"id": cls.grievance_ticket_1.admin2.id},
                "registration_data_import": {"id": None},
                "category": cls.grievance_ticket_1.category,
                "status": cls.grievance_ticket_1.status,
                "issue_type": None,
                "assigned_to": {"id": cls.user.id},
                "created_at": "2022-04-30T09:54:07.827000",
                "household_unicef_id": "HH-20-0000.0001",
                "priority": cls.grievance_ticket_1.priority,
                "urgency": cls.grievance_ticket_1.urgency,
                "grievance_type": "user",
                "ticket_details": {"household": {"head_of_household": {"family_name": "Kowalska_1"}}},
            },
        )

        cls.grievance_ticket_2 = GrievanceTicket.objects.create(
            **{
                "business_area": cls.business_area,
                "unicef_id": "GRV-0000002",
                "admin2": cls.admin_area_2,
                "language": "Polish",
                "consent": True,
                "description": "grievance_ticket_2",
                "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                "status": GrievanceTicket.STATUS_IN_PROGRESS,
                "issue_type": 12,
                "created_by": cls.user2,
                "assigned_to": cls.user2,
                "created_at": "2022-05-12T09:12:07.857000",
                "household_unicef_id": "HH-20-0000.0001",
                "priority": 2,
                "urgency": 3,
            }
        )

        cls.es.index(
            index="test_es_db",
            doc_type="_doc",
            id=cls.grievance_ticket_2.id,
            body={
                "business_area": {"slug": cls.grievance_ticket_2.business_area.name.lower()},
                "unicef_id": cls.grievance_ticket_2.unicef_id,
                "admin2": {"id": cls.grievance_ticket_2.admin2.id},
                "registration_data_import": {"id": "04992dce-154b-4938-8e47-74341541ebcf"},
                "category": cls.grievance_ticket_2.category,
                "status": cls.grievance_ticket_2.status,
                "issue_type": 3,
                "assigned_to": {"id": cls.user2.id},
                "created_at": "2022-05-12T09:12:07.857000",
                "household_unicef_id": "HH-20-0000.0002",
                "priority": cls.grievance_ticket_2.priority,
                "urgency": cls.grievance_ticket_2.urgency,
                "grievance_type": "user",
                "ticket_details": {"household": {"head_of_household": {"family_name": "Kowalska_2"}}},
            },
        )

        cls.grievance_ticket_3 = GrievanceTicket.objects.create(
            **{
                "business_area": cls.business_area,
                "unicef_id": "GRV-0000003",
                "admin2": cls.admin_area_2,
                "language": "Polish",
                "consent": True,
                "description": "grievance_ticket_3",
                "category": GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
                "status": GrievanceTicket.STATUS_ON_HOLD,
                "created_by": cls.user,
                "assigned_to": cls.user,
                "created_at": "2022-05-05T09:12:07.857000",
                "household_unicef_id": "HH-20-0000.0003",
                "priority": 3,
                "urgency": 1,
            }
        )

        cls.es.index(
            index="test_es_db",
            doc_type="_doc",
            id=cls.grievance_ticket_3.id,
            body={
                "business_area": {"slug": cls.grievance_ticket_3.business_area.name.lower()},
                "unicef_id": cls.grievance_ticket_3.unicef_id,
                "admin2": {"id": cls.grievance_ticket_3.admin2.id},
                "registration_data_import": {"id": None},
                "category": cls.grievance_ticket_3.category,
                "status": cls.grievance_ticket_3.status,
                "issue_type": None,
                "assigned_to": {"id": cls.user.id},
                "created_at": "2022-05-05T09:12:07.857000",
                "household_unicef_id": "HH-20-0000.0003",
                "priority": cls.grievance_ticket_3.priority,
                "urgency": cls.grievance_ticket_3.urgency,
                "grievance_type": "system",
                "ticket_details": {"household": {"head_of_household": {"family_name": "Kowalska_3"}}},
            },
        )

    @staticmethod
    def create_es_db():
        grievance_es_index = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "tests", "grievance_es_index.json"
        )

        with open(grievance_es_index) as f:
            es = Elasticsearch("http://elasticsearch:9200")
            es.indices.create(
                index="test_es_db",
                body={
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1,
                        "index.store.type": "mmapfs",
                    },
                    "mappings": json.load(f),
                },
            )

        return es

    @classmethod
    def tearDownClass(cls):
        es = Elasticsearch("http://elasticsearch:9200")
        es.indices.delete(index="test_es_db", ignore=[400, 404])
        super().tearDownClass()

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_unicef_id(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_SEARCH,
            context={"user": self.user},
            variables={"search": f"ticket_id {self.grievance_ticket_1.unicef_id}"},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_household_unicef_id(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_SEARCH,
            context={"user": self.user},
            variables={"search": "ticket_hh_id HH-20-0000.0003"},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_head_of_household_last_name(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_SEARCH,
            context={"user": self.user},
            variables={"search": "last_name Kowalska_1"},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_category(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CATEGORY,
            context={"user": self.user},
            variables={"category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_status(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_STATUS,
            context={"user": self.user},
            variables={"status": [GrievanceTicket.STATUS_NEW]},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_multiple_statuses(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_STATUS,
            context={"user": self.user},
            variables={"status": [GrievanceTicket.STATUS_ON_HOLD, GrievanceTicket.STATUS_IN_PROGRESS]},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_min_date_range(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CREATED_AT,
            context={"user": self.user},
            variables={"createdAtRange": '{"max":"2022-05-01"}'},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_max_date_range(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CREATED_AT,
            context={"user": self.user},
            variables={"createdAtRange": '{"min":"2022-05-10"}'},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_min_and_max_date_range(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CREATED_AT,
            context={"user": self.user},
            variables={"createdAtRange": '{"min":"2022-05-01","max":"2022-05-10"}'},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_admin(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_ADMIN_AREA,
            context={"user": self.user},
            variables={"admin": [self.admin_area_1.id]},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_issue_type(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_ISSUE_TYPE,
            context={"user": self.user},
            variables={"issueType": GrievanceTicket.ISSUE_TYPE_FRAUD_FORGERY},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_priority(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_PRIORITY,
            context={"user": self.user},
            variables={"priority": PRIORITY_LOW},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_urgency(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_URGENCY,
            context={"user": self.user},
            variables={"urgency": URGENCY_VERY_URGENT},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_assigned_to(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_ASSIGNED_TO,
            context={"user": self.user},
            variables={"assignedTo": self.id_to_base64(self.user2.id, "UserNode")},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_registration_data_import(self, mock_execute_test_es_query):
        self.maxDiff = None
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_REGISTRATION_DATA_IMPORT,
            context={"user": self.user},
            variables={
                "registrationDataImport": self.id_to_base64(
                    "04992dce-154b-4938-8e47-74341541ebcf", "RegistrationDataImportNode"
                )
            },
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_grievance_type(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_GRIEVANCE_TYPE,
            context={"user": self.user},
            variables={"grievanceType": "system"},
        )

    @patch("hct_mis_api.apps.grievance.filters.execute_es_query", side_effect=execute_test_es_query)
    def test_multiple_filters_should_return_grievance_1(self, mock_execute_test_es_query):
        self.maxDiff = None
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_MULTIPLE_FILTERS,
            context={"user": self.user},
            variables={
                "status": [GrievanceTicket.STATUS_NEW],
                "priority": PRIORITY_HIGH,
                "urgency": URGENCY_URGENT,
                "grievanceType": "user",
            },
        )
