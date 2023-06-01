import json
import re
from typing import TYPE_CHECKING, Any, Dict, Iterable, List

from django.db.models import Q, QuerySet
from django.db.models.functions import Lower

from constance import config
from django_filters import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
    OrderingFilter,
)

from hct_mis_api.apps.core.filters import (
    AgeRangeFilter,
    BusinessAreaSlugFilter,
    DateRangeFilter,
    IntegerRangeFilter,
)
from hct_mis_api.apps.core.utils import CustomOrderingFilter, decode_id_string
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.documents import HouseholdDocument, get_individual_doc
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    INDIVIDUAL_FLAGS_CHOICES,
    INDIVIDUAL_STATUS_CHOICES,
    NEEDS_ADJUDICATION,
    SANCTION_LIST_CONFIRMED_MATCH,
    SANCTION_LIST_POSSIBLE_MATCH,
    SEX_CHOICE,
    STATUS_ACTIVE,
    STATUS_DUPLICATE,
    STATUS_WITHDRAWN,
    Household,
    Individual,
)
from hct_mis_api.apps.program.models import Program

if TYPE_CHECKING:
    from hct_mis_api.apps.core.models import BusinessArea


def _prepare_kobo_asset_id_value(code: str) -> str:
    """
    preparing value for filter by kobo_asset_id
    value examples KOBO-111222, HOPE-20220531-3/111222, HOPE-2022530111222
    return asset_id number like 111222
    """
    if len(code) < 6:
        return code

    code = code[5:].split("/")[-1]  # remove prefix 'KOBO-' and split ['20220531-3', '111222']
    if code.startswith("20223"):
        # month 3 day 25...31 id is 44...12067
        code = code[7:]

    if code.startswith("20224"):
        # TODO: not sure if this one is correct?
        # code[5] is the day of month (or the first digit of it)
        # month 4 id is 12068..157380
        if len(code) == 12 and code[5] in ["1", "2", "3"]:
            code = code[-5:]
        else:
            code = code[-6:]

    if code.startswith("20225"):
        # month 5 id is 157381...392136
        code = code[-6:]

    if code.startswith("20226"):
        # month 6 id is 392137...
        code = code[-6:]
    return code


class HouseholdFilter(FilterSet):
    business_area = BusinessAreaSlugFilter()
    size = IntegerRangeFilter(field_name="size")
    search = CharFilter(method="search_filter")
    head_of_household__full_name = CharFilter(field_name="head_of_household__full_name", lookup_expr="startswith")
    last_registration_date = DateRangeFilter(field_name="last_registration_date")
    withdrawn = BooleanFilter(field_name="withdrawn")
    country_origin = CharFilter(field_name="country_origin__iso_code3", lookup_expr="startswith")

    class Meta:
        model = Household
        fields = {
            "business_area": ["exact"],
            "address": ["exact", "startswith"],
            "head_of_household__full_name": ["exact", "startswith"],
            "size": ["range", "lte", "gte"],
            "admin_area": ["exact"],
            "admin2": ["exact"],
            "target_populations": ["exact"],
            "programs": ["exact"],
            "residence_status": ["exact"],
            "withdrawn": ["exact"],
        }

    order_by = CustomOrderingFilter(
        fields=(
            "age",
            "sex",
            "household__id",
            "id",
            "unicef_id",
            "household_ca_id",
            "size",
            "status_label",
            Lower("head_of_household__full_name"),
            Lower("admin_area__name"),
            "residence_status",
            Lower("registration_data_import__name"),
            "total_cash_received",
            "last_registration_date",
            "first_registration_date",
        )
    )

    def _search_es(self, qs: QuerySet, value: Any) -> QuerySet:
        business_area = self.data["business_area"]
        query_dict = get_elasticsearch_query_for_households(value, business_area)
        es_response = (
            HouseholdDocument.search().params(search_type="dfs_query_then_fetch").update_from_dict(query_dict).execute()
        )
        es_ids = [x.meta["id"] for x in es_response]

        split_values_list = value.split(" ")
        inner_query = Q()
        for split_value in split_values_list:
            striped_value = split_value.strip(",")
            if striped_value.startswith(("HOPE-", "KOBO-")):
                _value = _prepare_kobo_asset_id_value(value)
                # if user put somethink like 'KOBO-111222', 'HOPE-20220531-3/111222', 'HOPE-2022531111222'
                # will filter by '111222' like 111222 is ID
                inner_query |= Q(kobo_asset_id__endswith=_value)
        return qs.filter(Q(id__in=es_ids) | inner_query).distinct()

    def search_filter(self, qs: QuerySet, name: str, value: Any) -> QuerySet:
        if config.USE_ELASTICSEARCH_FOR_HOUSEHOLDS_SEARCH:
            return self._search_es(qs, value)
        return self._search_db(qs, value)

    def _search_db(self, qs: QuerySet, value: str) -> QuerySet:
        if re.match(r"([\"\']).+\1", value):
            values = [value.replace('"', "").strip()]
        else:
            values = value.split(" ")
        q_obj = Q()
        for value in values:
            value = value.strip(",")
            inner_query = Q()
            inner_query |= Q(head_of_household__full_name__istartswith=value)
            inner_query |= Q(head_of_household__given_name__istartswith=value)
            inner_query |= Q(head_of_household__middle_name__istartswith=value)
            inner_query |= Q(head_of_household__family_name__istartswith=value)
            inner_query |= Q(residence_status__istartswith=value)
            inner_query |= Q(admin_area__name__istartswith=value)
            inner_query |= Q(unicef_id__istartswith=value)
            inner_query |= Q(unicef_id__iendswith=value)
            if value.startswith(("HOPE-", "KOBO-")):
                _value = _prepare_kobo_asset_id_value(value)
                # if user put something like 'KOBO-111222', 'HOPE-20220531-3/111222', 'HOPE-2022531111222'
                # will filter by '111222' like 111222 is ID
                inner_query |= Q(kobo_asset_id__endswith=_value)
            q_obj &= inner_query
        return qs.filter(q_obj).distinct()


class IndividualFilter(FilterSet):
    business_area = BusinessAreaSlugFilter()
    age = AgeRangeFilter(field_name="birth_date")
    sex = MultipleChoiceFilter(field_name="sex", choices=SEX_CHOICE)
    programs = ModelMultipleChoiceFilter(field_name="household__programs", queryset=Program.objects.all())
    search = CharFilter(method="search_filter")
    last_registration_date = DateRangeFilter(field_name="last_registration_date")
    admin2 = ModelMultipleChoiceFilter(
        field_name="household__admin_area", queryset=Area.objects.filter(area_type__area_level=2)
    )
    status = MultipleChoiceFilter(choices=INDIVIDUAL_STATUS_CHOICES, method="status_filter")
    excluded_id = CharFilter(method="filter_excluded_id")
    withdrawn = BooleanFilter(field_name="withdrawn")
    flags = MultipleChoiceFilter(choices=INDIVIDUAL_FLAGS_CHOICES, method="flags_filter")

    class Meta:
        model = Individual
        fields = {
            "household__id": ["exact"],
            "business_area": ["exact"],
            "full_name": ["exact", "startswith", "endswith"],
            "sex": ["exact"],
            "household__admin_area": ["exact"],
            "withdrawn": ["exact"],
        }

    order_by = CustomOrderingFilter(
        fields=(
            "id",
            "unicef_id",
            Lower("full_name"),
            "household__id",
            "household__unicef_id",
            "birth_date",
            "sex",
            "relationship",
            Lower("household__admin_area__name"),
            "last_registration_date",
            "first_registration_date",
        )
    )

    def flags_filter(self, qs: QuerySet, name: str, value: List[str]) -> QuerySet:
        q_obj = Q()
        if NEEDS_ADJUDICATION in value:
            q_obj |= Q(deduplication_golden_record_status=NEEDS_ADJUDICATION)
        if DUPLICATE in value:
            q_obj |= Q(duplicate=True)
        if SANCTION_LIST_POSSIBLE_MATCH in value:
            q_obj |= Q(sanction_list_possible_match=True, sanction_list_confirmed_match=False)
        if SANCTION_LIST_CONFIRMED_MATCH in value:
            q_obj |= Q(sanction_list_confirmed_match=True)

        return qs.filter(q_obj)

    def _search_es(self, qs: QuerySet, value: str) -> QuerySet:
        business_area = self.data["business_area"]
        query_dict = get_elasticsearch_query_for_individuals(value, business_area)
        es_response = (
            get_individual_doc(business_area)
            .search()
            .params(search_type="dfs_query_then_fetch")
            .update_from_dict(query_dict)
            .execute()
        )

        es_ids = [x.meta["id"] for x in es_response]
        return qs.filter(Q(id__in=es_ids)).distinct()

    def search_filter(self, qs: QuerySet, name: str, value: Any) -> QuerySet:
        if value.upper().startswith("IND-"):
            return qs.filter(unicef_id__istartswith=value)
        if config.USE_ELASTICSEARCH_FOR_INDIVIDUALS_SEARCH:
            return self._search_es(qs, value)
        return self._search_db(qs, value)

    def _search_db(self, qs: QuerySet, value: str) -> QuerySet:
        if re.match(r"([\"\']).+\1", value):
            values = [value.replace('"', "").strip()]
        else:
            values = value.split(" ")
        q_obj = Q()
        for value in values:
            inner_query = Q(household__admin_area__name__istartswith=value)
            inner_query |= Q(unicef_id__istartswith=value)
            inner_query |= Q(unicef_id__iendswith=value)
            inner_query |= Q(household__unicef_id__istartswith=value)
            inner_query |= Q(full_name__istartswith=value)
            inner_query |= Q(given_name__istartswith=value)
            inner_query |= Q(middle_name__istartswith=value)
            inner_query |= Q(family_name__istartswith=value)
            inner_query |= Q(documents__document_number__istartswith=value)
            inner_query |= Q(phone_no__istartswith=value)
            inner_query |= Q(phone_no_alternative__istartswith=value)
            q_obj &= inner_query
        return qs.filter(q_obj).distinct()

    def status_filter(self, qs: QuerySet, name: str, value: List[str]) -> QuerySet:
        q_obj = Q()
        if STATUS_DUPLICATE in value:
            q_obj |= Q(duplicate=True)
        if STATUS_WITHDRAWN in value:
            q_obj |= Q(withdrawn=True)
        if STATUS_ACTIVE in value:
            q_obj |= Q(duplicate=False, withdrawn=False)

        return qs.filter(q_obj).distinct()

    def filter_excluded_id(self, qs: QuerySet, name: str, value: Any) -> QuerySet:
        return qs.exclude(id=decode_id_string(value))


def get_elasticsearch_query_for_individuals(value: str, business_area: "BusinessArea") -> Dict:
    match_fields = [
        "phone_no_text",
        "phone_no_alternative",
        "documents.number",
        "admin1",
        "admin2",
    ]
    prefix_fields = [
        "middle_name",
        "unicef_id",
        "household.unicef_id",
        "phone_no_text",
    ]
    wildcard_fields = ["phone_no", "unicef_id", "household.unicef_id"]

    match_queries: Iterable = [
        {
            "match": {
                x: {
                    "query": value,
                }
            }
        }
        for x in match_fields
    ]
    prefix_queries: Iterable = [
        {
            "match_phrase_prefix": {
                x: {
                    "query": value,
                }
            }
        }
        for x in prefix_fields
    ]
    wildcard_queries: Iterable = [
        {
            "wildcard": {
                x: {
                    "value": f"*{value}",
                }
            }
        }
        for x in wildcard_fields
    ]
    all_queries: List = []
    all_queries.extend(wildcard_queries)
    all_queries.extend(prefix_queries)
    all_queries.extend(match_queries)

    values = value.split(" ")
    if len(values) == 2:
        all_queries.append(
            {
                "bool": {
                    "must": [
                        {
                            "match_phrase_prefix": {
                                "given_name": {
                                    "query": values[0],
                                }
                            }
                        },
                        {
                            "match_phrase_prefix": {
                                "family_name": {
                                    "query": values[1],
                                }
                            }
                        },
                    ],
                },
            }
        )
    elif len(values) == 1:
        all_queries.append(
            {
                "match_phrase_prefix": {
                    "given_name": {
                        "query": value,
                        "boost": 1.1,
                    }
                }
            }
        )
        all_queries.append(
            {
                "match_phrase_prefix": {
                    "family_name": {
                        "query": value,
                        "boost": 1.1,
                    }
                }
            },
        )
    else:
        all_queries.append(
            {
                "match_phrase_prefix": {
                    "full_name": {
                        "query": value,
                    }
                }
            },
        )

    query = {
        "size": "100",
        "_source": False,
        "query": {
            "bool": {
                "filter": {"term": {"business_area": business_area}},
                "minimum_should_match": 1,
                "should": all_queries,
            }
        },
    }
    json.dumps(query)
    return query


def get_elasticsearch_query_for_households(value: Any, business_area: "BusinessArea") -> Dict:
    match_fields = [
        "admin1",
        "admin2",
    ]
    prefix_fields = ["head_of_household.middle_name", "unicef_id", "residence_status"]
    wildcard_fields = ["unicef_id"]
    match_queries: Iterable = [
        {
            "match": {
                x: {
                    "query": value,
                }
            }
        }
        for x in match_fields
    ]
    prefix_queries: Iterable = [
        {
            "match_phrase_prefix": {
                x: {
                    "query": value,
                }
            }
        }
        for x in prefix_fields
    ]
    wildcard_queries: Iterable = [
        {
            "wildcard": {
                x: {
                    "value": f"*{value}",
                }
            }
        }
        for x in wildcard_fields
    ]
    all_queries: List = []
    all_queries.extend(wildcard_queries)
    all_queries.extend(prefix_queries)
    all_queries.extend(match_queries)

    values = value.split(" ")
    if len(values) == 2:
        all_queries.append(
            {
                "bool": {
                    "must": [
                        {
                            "match_phrase_prefix": {
                                "head_of_household.given_name": {
                                    "query": values[0],
                                }
                            }
                        },
                        {
                            "match_phrase_prefix": {
                                "head_of_household.family_name": {
                                    "query": values[1],
                                }
                            }
                        },
                    ],
                },
            }
        )
    elif len(values) == 1:
        all_queries.append(
            {
                "match_phrase_prefix": {
                    "head_of_household.given_name": {
                        "query": value,
                        "boost": 1.1,
                    }
                }
            }
        )
        all_queries.append(
            {
                "match_phrase_prefix": {
                    "head_of_household.family_name": {
                        "query": value,
                        "boost": 1.1,
                    }
                }
            },
        )
    else:
        all_queries.append(
            {
                "match_phrase_prefix": {
                    "head_of_household.full_name": {
                        "query": value,
                    }
                }
            },
        )

    query: Dict[str, Any] = {
        "size": "100",
        "_source": False,
        "query": {
            "bool": {
                "minimum_should_match": 1,
                "should": all_queries,
            }
        },
    }
    if config.USE_ELASTICSEARCH_FOR_HOUSEHOLDS_SEARCH_USE_BUSINESS_AREA:
        query["query"]["bool"]["filter"] = ({"term": {"business_area": business_area}},)
    return query


class MergedHouseholdFilter(FilterSet):
    """
    This filter emulates ImportedHousehold filter for data structure which is linked to Import Preview when RDI is merged
    """

    business_area = CharFilter(field_name="business_area__slug")
    rdi_id = CharFilter(method="filter_rdi_id")

    class Meta:
        model = Household
        fields = ()

    order_by = CustomOrderingFilter(
        fields=(
            "id",
            Lower("head_of_household__full_name"),
            "size",
            "first_registration_date",
            "admin2_title",
        )
    )

    def filter_rdi_id(self, queryset: "QuerySet", model_field: Any, value: str) -> "QuerySet":
        return queryset.filter(registration_data_import_id=decode_id_string(value))


class MergedIndividualFilter(FilterSet):
    rdi_id = CharFilter(method="filter_rdi_id")
    duplicates_only = BooleanFilter(method="filter_duplicates_only")
    business_area = CharFilter(field_name="business_area__slug")

    class Meta:
        model = Individual
        fields = ("household",)

    order_by = OrderingFilter(
        fields=(
            "unicef_id",
            "id",
            "full_name",
            "birth_date",
            "sex",
            "deduplication_batch_status",
            "deduplication_golden_record_status",
        )
    )

    def filter_rdi_id(self, queryset: "QuerySet", model_field: Any, value: str) -> "QuerySet":
        return queryset.filter(registration_data_import_id=decode_id_string(value))

    def filter_duplicates_only(self, queryset: "QuerySet", model_field: Any, value: bool) -> "QuerySet":
        if value:
            return queryset.filter(
                Q(deduplication_golden_record_status=DUPLICATE) | Q(deduplication_batch_status=DUPLICATE_IN_BATCH)
            )
        return queryset
