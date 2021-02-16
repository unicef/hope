from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from hct_mis_api.apps.core.es_analyzers import phonetic_analyzer, name_synonym_analyzer
from .elasticsearch_utils import DEFAULT_SCRIPT
from .models import Individual


@registry.register_document
class IndividualDocument(Document):
    id = fields.KeywordField(boost=0)
    given_name = fields.TextField(
        analyzer=name_synonym_analyzer, fields={"phonetic": fields.TextField(analyzer=phonetic_analyzer)}
    )
    middle_name = fields.TextField(analyzer=phonetic_analyzer)
    family_name = fields.TextField(fields={"phonetic": fields.TextField(analyzer=phonetic_analyzer)})
    full_name = fields.TextField(analyzer=phonetic_analyzer)
    birth_date = fields.DateField(similarity="boolean")
    phone_no = fields.KeywordField("phone_no.__str__", similarity="boolean")
    phone_no_alternative = fields.KeywordField("phone_no_alternative.__str__", similarity="boolean")
    business_area = fields.KeywordField(similarity="boolean")
    admin1 = fields.KeywordField()
    admin2 = fields.KeywordField()
    household = fields.ObjectField(
        properties={
            "residence_status": fields.KeywordField(similarity="boolean"),
            "country_origin": fields.KeywordField(attr="country_origin.alpha3", similarity="boolean"),
            "size": fields.IntegerField(),
            "address": fields.TextField(),
            "country": fields.KeywordField(attr="country.alpha3", similarity="boolean"),
            "female_age_group_0_5_count": fields.IntegerField(),
            "female_age_group_6_11_count": fields.IntegerField(),
            "female_age_group_12_17_count": fields.IntegerField(),
            "female_age_group_18_59_count": fields.IntegerField(),
            "female_age_group_60_count": fields.IntegerField(),
            "pregnant_count": fields.IntegerField(),
            "male_age_group_0_5_count": fields.IntegerField(),
            "male_age_group_6_11_count": fields.IntegerField(),
            "male_age_group_12_17_count": fields.IntegerField(),
            "male_age_group_18_59_count": fields.IntegerField(),
            "male_age_group_60_count": fields.IntegerField(),
            "female_age_group_0_5_disabled_count": fields.IntegerField(),
            "female_age_group_6_11_disabled_count": fields.IntegerField(),
            "female_age_group_12_17_disabled_count": fields.IntegerField(),
            "female_age_group_18_59_disabled_count": fields.IntegerField(),
            "female_age_group_60_disabled_count": fields.IntegerField(),
            "male_age_group_0_5_disabled_count": fields.IntegerField(),
            "male_age_group_6_11_disabled_count": fields.IntegerField(),
            "male_age_group_12_17_disabled_count": fields.IntegerField(),
            "male_age_group_18_59_disabled_count": fields.IntegerField(),
            "male_age_group_60_disabled_count": fields.IntegerField(),
            "head_of_household": fields.KeywordField(attr="head_of_household.id", similarity="boolean"),
            "returnee": fields.BooleanField(),
            "registration_method": fields.KeywordField(similarity="boolean"),
            "collect_individual_data": fields.KeywordField(similarity="boolean"),
            "currency": fields.KeywordField(similarity="boolean"),
            "unhcr_id": fields.KeywordField(similarity="boolean"),
        }
    )
    documents = fields.ObjectField(
        properties={
            "number": fields.KeywordField(attr="document_number", similarity="boolean"),
            "type": fields.KeywordField(attr="type.type", similarity="boolean"),
            "country": fields.KeywordField(attr="type.country.alpha3", similarity="boolean"),
        }
    )
    identities = fields.ObjectField(
        properties={
            "number": fields.KeywordField(similarity="boolean"),
            "agency": fields.KeywordField(attr="agency.type", similarity="boolean"),
        }
    )
    households_and_roles = fields.ObjectField(
        properties={
            "role": fields.KeywordField(similarity="boolean"),
            "individual": fields.KeywordField(attr="individual.id", similarity="boolean"),
        }
    )

    def prepare_admin1(self, instance):
        household = instance.household
        if household:
            admin_area = household.admin_area
            if admin_area:
                return admin_area.title
            return

    def prepare_admin2(self, instance):
        household = instance.household
        if household:
            admin_area = household.admin_area
            if admin_area:
                children = admin_area.children.filter(admin_area_level__admin_level=2).first()
                if children:
                    return children.title
                return

    def prepare_hash_key(self, instance):
        return instance.get_hash_key

    def prepare_business_area(self, instance):
        return instance.business_area.slug

    class Index:
        name = "individuals"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "similarity": {
                "default": {
                    "type": "scripted",
                    "script": {
                        "source": DEFAULT_SCRIPT,
                    },
                },
            },
        }

    class Django:
        model = Individual

        fields = [
            "relationship",
            "sex",
            "created_at",
            "updated_at",
        ]
