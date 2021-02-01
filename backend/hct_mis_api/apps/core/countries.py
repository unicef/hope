from django_countries import Countries as InternalCountries

from hct_mis_api.apps.core.utils import CaseInsensitiveTuple


class Countries:
    @classmethod
    def get_countries(cls):
        countries_instance = InternalCountries()
        return [
            (label, alpha2, countries_instance.alpha3(alpha2)) for alpha2, label in countries_instance.countries.items()
        ]

    @classmethod
    def get_choices(cls, output_code="alpha2") -> list:
        if output_code not in ("alpha2", "alpha3"):
            raise ValueError("output_code have to be one of: alpha2, alpha3")
        return [
            {"label": {"English(EN)": name}, "value": alpha2 if output_code == "alpha2" else alpha3}
            for name, alpha2, alpha3 in cls.get_countries()
        ]

    @classmethod
    def is_valid_country_choice(cls, choice: str) -> bool:
        return any(choice in CaseInsensitiveTuple(country_tuple) for country_tuple in cls.get_countries())

    @classmethod
    def get_country_value(cls, input_value: str, output_type: str = "alpha2", *args, **kwargs) -> str:
        index_map = {
            "name": 0,
            "alpha2": 1,
            "alpha3": 2,
        }

        if output_type not in ("name", "alpha2", "alpha3"):
            raise ValueError("output_type have to be one of: name, alpha2, alpha3")

        for country_tuple in cls.get_countries():
            if input_value in CaseInsensitiveTuple(country_tuple):
                return country_tuple[index_map[output_type]]
