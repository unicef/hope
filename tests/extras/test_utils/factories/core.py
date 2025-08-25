import random
from typing import Any, List

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hope.models.core import (
    BusinessArea,
    CountryCodeMap,
    DataCollectingType,
    FlexibleAttribute,
    FlexibleAttributeGroup,
    PeriodicFieldData,
    StorageFile,
)
from hope.models.geo import Country
from hope.apps.periodic_data_update.utils import field_label_to_field_name
from hope.models.program import Program

faker = Faker()


def create_afghanistan() -> BusinessArea:
    return BusinessArea.objects.get_or_create(
        code="0060",
        defaults={
            "code": "0060",
            "name": "Afghanistan",
            "long_name": "THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            "region_code": "64",
            "region_name": "SAR",
            "slug": "afghanistan",
            "has_data_sharing_agreement": True,
            "kobo_token": "XXX",
        },
    )[0]


def create_ukraine() -> BusinessArea:
    return BusinessArea.objects.create(
        code="4410",
        name="Ukraine",
        long_name="UKRAINE",
        region_code="66",
        region_name="ECAR",
        slug="ukraine",
        has_data_sharing_agreement=True,
        kobo_token="YYY",
    )


def create_kenya() -> BusinessArea:
    return BusinessArea.objects.create(
        code="2400",
        name="Kenya",
        long_name="THE REPUBLIC OF KENYA",
        region_code="63",
        region_name="ESAR",
        slug="kenya",
        has_data_sharing_agreement=True,
        kobo_token="ZZZ",
    )


class StorageFileFactory(DjangoModelFactory):
    class Meta:
        model = StorageFile

    business_area = factory.LazyAttribute(lambda _: BusinessArea.objects.first())


class DataCollectingTypeFactory(DjangoModelFactory):
    class Meta:
        model = DataCollectingType
        django_get_or_create = ("label", "code")

    label = factory.Faker("text", max_nb_chars=30)
    code = factory.Faker("text", max_nb_chars=30)
    type = DataCollectingType.Type.STANDARD
    description = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    individual_filters_available = True
    household_filters_available = True

    @factory.post_generation
    def business_areas(self, create: Any, extracted: List[Any], **kwargs: Any) -> None:
        if not create:
            return

        if extracted:
            for business_area in extracted:
                self.limit_to.add(business_area)


class PeriodicFieldDataFactory(DjangoModelFactory):
    subtype = fuzzy.FuzzyChoice([choice[0] for choice in PeriodicFieldData.TYPE_CHOICES])
    rounds_names = factory.LazyAttribute(
        lambda _: [factory.Faker("word").evaluate(None, None, {"locale": None}) for _ in range(random.randint(1, 10))]
    )
    number_of_rounds = factory.LazyAttribute(lambda o: len(o.rounds_names))

    class Meta:
        model = PeriodicFieldData


class FlexibleAttributeForPDUFactory(DjangoModelFactory):
    associated_with = FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL
    label = factory.Faker("word")
    name = factory.LazyAttribute(lambda instance: field_label_to_field_name(instance.label))
    type = FlexibleAttribute.PDU
    pdu_data = factory.SubFactory(PeriodicFieldDataFactory)

    class Meta:
        model = FlexibleAttribute

    @factory.lazy_attribute
    def program(self) -> Any:
        from extras.test_utils.factories.program import ProgramFactory

        return ProgramFactory()

    @classmethod
    def _create(cls, target_class: Any, *args: Any, **kwargs: Any) -> FlexibleAttribute:
        label = kwargs.pop("label", None)
        kwargs["label"] = {"English(EN)": label}
        return super()._create(target_class, *args, **kwargs)


def create_pdu_flexible_attribute(
    label: str,
    subtype: str,
    number_of_rounds: int,
    rounds_names: list[str],
    program: Program,
) -> FlexibleAttribute:
    name = field_label_to_field_name(label)
    flexible_attribute = FlexibleAttribute.objects.create(
        type=FlexibleAttribute.PDU,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        label={"English(EN)": label},
        name=name,
        program=program,
    )
    flexible_attribute.pdu_data = PeriodicFieldData.objects.create(
        subtype=subtype, number_of_rounds=number_of_rounds, rounds_names=rounds_names
    )
    flexible_attribute.save()
    return flexible_attribute


def generate_country_codes() -> None:
    for country in Country.objects.all():
        CountryCodeMap.objects.get_or_create(country=country, defaults={"ca_code": country.iso_code3})


business_area_short_name_code_map = {
    "Analysis,Planning & Monitoring": "456C",
    "Timor-Leste": "7060",
    "Morocco": "2910",
    "Zambia": "4980",
    "Public Partnerships Division": "456I",
    "Malaysia": "2700",
    "Paraguay": "3360",
    "Nicaragua": "3120",
    "Kazakhstan": "2390",
    "Kosovo": "8971",
    "Kenya": "2400",
    "Cote D'Ivoire": "2250",
    "Albania": "0090",
    "Guinea": "1770",
    "Rep of Uzbekistan": "4630",
    "Dominican Republic": "1260",
    "Saudi Arabia": "3780",
    "Denmark": "1200",
    "EAPRO, Thailand": "420R",
    "Thailand": "4200",
    "Armenia": "0260",
    "Ecuador": "1350",
    "Liberia": "2550",
    "Democratic Republic of Congo": "0990",
    "Barbados": "0420",
    "Lebanon": "2490",
    "Angola": "6810",
    "Nepal": "2970",
    "Tajikistan": "4150",
    "El Salvador": "1380",
    "Costa Rica": "1020",
    "Evaluation Office": "456O",
    "Gabon": "1530",
    "GSSC Project": "456Q",
    "Division of Human Resources": "456K",
    "Research Division": "456E",
    "Chad": "0810",
    "Mongolia": "2880",
    "Syria": "4140",
    "LACRO, Panama": "333R",
    "Sudan": "4020",
    "Republic of Montenegro": "8950",
    "OSEB": "456S",
    "Republic of Mozambique": "6890",
    "Ukraine": "4410",
    "Yemen": "4920",
    "Turkey": "4350",
    "Division of Communication": "456G",
    "United Rep. of Tanzania": "4550",
    "Off of Global Insight & Policy": "456R",
    "Venezuela": "4710",
    "Bulgaria": "0570",
    "Executive Director's Office": "456B",
    "Croatia": "1030",
    "Belize": "6110",
    "Eswatini": "4030",
    "Azerbaijan": "0310",
    "Sierra Leone": "3900",
    "Switzerland": "5750",
    "Cambodia": "0660",
    "Mali": "2760",
    "Sri Lanka": "0780",
    "Romania": "3660",
    "Benin": "1170",
    "Georgia": "1600",
    "ROSA, Nepal": "297R",
    "Info & Comm Technology Div": "456L",
    "Oman": "6350",
    "Guinea Bissau": "6850",
    "Argentina": "0240",
    "Madagascar": "2670",
    "Office of Global Innovation": "240B",
    "Jordan": "2340",
    "Rwanda": "3750",
    "Central African Republic": "0750",
    "Lesotho": "2520",
    "Sao Tome & Principe": "6830",
    "Senegal": "3810",
    "ECARO, Switzerland": "575R",
    "Egypt": "4500",
    "Niger": "3180",
    "Somalia": "3920",
    "Nigeria": "3210",
    "Field Sup & Coordination Off": "456P",
    "Office of Research, Italy": "2220",
    "Zimbabwe": "6260",
    "Chile": "0840",
    "Malawi": "2690",
    "Botswana": "0520",
    "Eritrea": "1420",
    "Lao People's Dem Rep.": "2460",
    "Belarus": "0630",
    "Republic of Cameroon": "0690",
    "Namibia": "6980",
    "Moldova": "5640",
    "Iraq": "2130",
    "Office of Emergency Prog.": "456F",
    "Iran": "2100",
    "Papua New Guinea": "6490",
    "Maldives": "2740",
    "Burundi": "0610",
    "Panama": "3330",
    "China": "0860",
    "Mexico": "2850",
    "Vietnam": "5200",
    "Turkmenistan": "4360",
    "ESARO, Kenya": "240R",
    "Equatorial Guinea": "1390",
    "Indonesia": "2070",
    "Procurement Services": "120X",
    "India": "2040",
    "Czech Republic": "BOCZ",
    "Colombia": "0930",
    "Mauritania": "2820",
    "Bhutan": "0490",
    "Comoros": "6620",
    "Global Shared Services Centre": "1950",
    "Ethiopia": "1410",
    "Int. Audit & Invest (OIAI)": "456N",
    "Programme Division": "456D",
    "Gov. & Multilateral Affairs": "456H",
    "WCARO, Senegal": "381R",
    "Brazil": "0540",
    "DP Republic of Korea": "5150",
    "Pakistan": "3300",
    "MENA, Jordan": "234R",
    "Bangladesh": "5070",
    "Div. of Finance & Admin Mgmt": "456J",
    "Cabo Verde": "6820",
    "Jamaica": "2280",
    "Cuba": "1050",
    "Afghanistan": "0060",
    "Haiti": "1830",
    "Gambia": "1560",
    "UNICEF Hosted Funds": "456T",
    "Djibouti": "6690",
    "Tunisia": "4320",
    "South Africa": "3930",
    "Togo": "4230",
    "South Sudan": "4040",
    "Peru": "3390",
    "Bolivia": "0510",
    "Guyana": "1800",
    "Myanmar": "0600",
    "Uganda": "4380",
    "Honduras": "1860",
    "Fiji (Pacific Islands)": "1430",
    "Libya": "2580",
    "Global": "GLOBAL",
    "Palestine, State of": "7050",
    "North Macedonia": "2660",
    "Ghana": "1620",
    "Serbia": "8970",
    "Geneva Common Services": "575C",
    "Algeria": "0120",
    "Republic of Kyrgyzstan": "2450",
    "Bosnia and Herzegovina": "0530",
    "Congo": "3380",
    "Philippines": "3420",
    "Burkina Faso": "4590",
    "Russia": "3700",
    "Guatemala": "1680",
    "Uruguay": "4620",
}


def generate_business_areas() -> None:
    for country_name, ba_code in business_area_short_name_code_map.items():
        if country := Country.objects.filter(short_name=country_name).first():
            business_area, _ = BusinessArea.objects.get_or_create(
                code=ba_code,
                defaults={
                    "name": country.short_name,
                    "long_name": country.name,
                    "region_code": country.iso_num,
                    "region_name": country.iso_code3,
                    "has_data_sharing_agreement": True,
                    "active": True,
                    "kobo_token": "abc_test",
                    "is_accountability_applicable": True,
                },
            )
            business_area.countries.add(country)

    # create Global
    BusinessArea.objects.get_or_create(
        code="GLOBAL",
        defaults={
            "name": "Global",
            "long_name": "Global Business Area",
            "region_code": "GLOBAL",
            "region_name": "GLOBAL",
            "has_data_sharing_agreement": True,
        },
    )


def generate_data_collecting_types() -> None:
    all_ba_id_list = list(BusinessArea.objects.all().values_list("id", flat=True))
    data_collecting_types = [
        {
            "label": "Partial",
            "code": "partial_individuals",
            "description": "Partial individuals collected",
            "type": DataCollectingType.Type.SOCIAL.value,
        },
        {
            "label": "Full",
            "code": "full_collection",
            "description": "Full individual collected",
            "type": DataCollectingType.Type.STANDARD.value,
        },
        {
            "label": "Size only",
            "code": "size_only",
            "description": "Size only collected",
            "type": DataCollectingType.Type.STANDARD.value,
        },
        {
            "label": "size/age/gender disaggregated",
            "code": "size_age_gender_disaggregated",
            "description": "No individual data",
            "type": DataCollectingType.Type.SOCIAL.value,
        },
    ]

    for data_dict in data_collecting_types:
        DataCollectingTypeFactory(
            label=data_dict["label"],
            code=data_dict["code"],
            business_areas=all_ba_id_list,
            type=data_dict["type"],
            household_filters_available=bool(data_dict["type"] == DataCollectingType.Type.STANDARD.value),
        )


def generate_pdu_data() -> None:
    test_program = Program.objects.get(business_area__slug="afghanistan", name="Test Program")
    group = FlexibleAttributeGroup.objects.create(name="Group 1", label={"english": "english"})
    pdu_data = PeriodicFieldData.objects.create(
        subtype="STRING",
        number_of_rounds=12,
        rounds_names=["test1", "test2", "test3..."],
    )
    FlexibleAttributeForPDUFactory(
        name="test_1_i_f",
        program=test_program,
        pdu_data=pdu_data,
        label={"English(EN)": "Test pdu 1"},
        hint={"English(EN)": "Test pdu 1"},
        group=group,
    )
