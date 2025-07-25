import logging
from functools import cache
from typing import Any

from django_countries import countries as internal_countries
from django_countries.fields import Country

from hct_mis_api.apps.core.utils import CaseInsensitiveTuple

logger = logging.getLogger(__name__)


class Countries:
    @classmethod
    @cache
    def get_countries(cls) -> list[tuple[str, str, str]]:
        return [(label, alpha2, Country(alpha2).alpha3) for alpha2, label in internal_countries]

    @classmethod
    def get_choices(cls, output_code: str = "alpha2") -> list:
        if output_code not in ("alpha2", "alpha3"):
            logger.warning(f"output_code have to be one of: alpha2, alpha3, provided output_code={output_code}")
            raise ValueError("output_code have to be one of: alpha2, alpha3")
        return [
            {"label": {"English(EN)": name}, "value": alpha2 if output_code == "alpha2" else alpha3}
            for name, alpha2, alpha3 in cls.get_countries()
        ]

    @classmethod
    @cache
    def is_valid_country_choice(cls, choice: str) -> bool:
        return any(choice in CaseInsensitiveTuple(country_tuple) for country_tuple in cls.get_countries())

    @classmethod
    def get_country_value(cls, input_value: str, output_type: str = "alpha2", *args: Any, **kwargs: Any) -> str | None:
        index_map = {
            "name": 0,
            "alpha2": 1,
            "alpha3": 2,
        }

        if output_type not in ("name", "alpha2", "alpha3"):
            logger.warning(f"output_type have to be one of: name, alpha2, alpha3, provided output_type={output_type}")
            raise ValueError("output_type have to be one of: name, alpha2, alpha3")

        for country_tuple in cls.get_countries():
            if input_value in CaseInsensitiveTuple(country_tuple):
                return country_tuple[index_map[output_type]]

        return None


class SanctionListCountries:
    COUNTRIES = {
        (
            "Afghanistan",
            "AF",
            "AFG",
        ),
        (
            "Albania",
            "AL",
            "ALB",
        ),
        (
            "Algeria",
            "DZ",
            "DZA",
        ),
        (
            "American Samoa",
            "AS",
            "ASM",
        ),
        (
            "Andorra",
            "AD",
            "AND",
        ),
        (
            "Angola",
            "AO",
            "AGO",
        ),
        (
            "Anguilla",
            "AI",
            "AIA",
        ),
        (
            "Antarctica",
            "AQ",
            "ATA",
        ),
        (
            "Antigua and Barbuda",
            "AG",
            "ATG",
        ),
        (
            "Argentina",
            "AR",
            "ARG",
        ),
        (
            "Armenia",
            "AM",
            "ARM",
        ),
        (
            "Aruba",
            "AW",
            "ABW",
        ),
        (
            "Australia",
            "AU",
            "AUS",
        ),
        (
            "Austria",
            "AT",
            "AUT",
        ),
        (
            "Azerbaijan",
            "AZ",
            "AZE",
        ),
        (
            "Bahamas",
            "BS",
            "BHS",
        ),
        (
            "Bahrain",
            "BH",
            "BHR",
        ),
        (
            "Bangladesh",
            "BD",
            "BGD",
        ),
        (
            "Barbados",
            "BB",
            "BRB",
        ),
        (
            "Belarus",
            "BY",
            "BLR",
        ),
        (
            "Belgium",
            "BE",
            "BEL",
        ),
        (
            "Belize",
            "BZ",
            "BLZ",
        ),
        (
            "Benin",
            "BJ",
            "BEN",
        ),
        (
            "Bermuda",
            "BM",
            "BMU",
        ),
        (
            "Bhutan",
            "BT",
            "BTN",
        ),
        (
            "Bolivia",
            "BO",
            "BOL",
        ),
        (
            "Bosnia and Herzegovina",
            "BA",
            "BIH",
        ),
        (
            "Botswana",
            "BW",
            "BWA",
        ),
        (
            "Bouvet Island",
            "BV",
            "BVT",
        ),
        (
            "Brazil",
            "BR",
            "BRA",
        ),
        (
            "British Indian Ocean Territory",
            "IO",
            "IOT",
        ),
        (
            "Brunei",
            "BN",
            "BRN",
        ),
        (
            "Bulgaria",
            "BG",
            "BGR",
        ),
        (
            "Burkina Faso",
            "BF",
            "BFA",
        ),
        (
            "Burundi",
            "BI",
            "BDI",
        ),
        (
            "Cambodia",
            "KH",
            "KHM",
        ),
        (
            "Cameroon",
            "CM",
            "CMR",
        ),
        (
            "Canada",
            "CA",
            "CAN",
        ),
        (
            "Cape Verde",
            "CV",
            "CPV",
        ),
        (
            "Cayman Islands",
            "KY",
            "CYM",
        ),
        (
            "Central African Republic",
            "CF",
            "CAF",
        ),
        (
            "Chad",
            "TD",
            "TCD",
        ),
        (
            "Chile",
            "CL",
            "CHL",
        ),
        (
            "China",
            "CN",
            "CHN",
        ),
        (
            "Christmas Island",
            "CX",
            "CXR",
        ),
        (
            "Cocos (Keeling) Islands",
            "CC",
            "CCK",
        ),
        (
            "Colombia",
            "CO",
            "COL",
        ),
        (
            "Comoros",
            "KM",
            "COM",
        ),
        (
            "Congo",
            "CG",
            "COG",
        ),
        (
            "The Democratic Republic of the Congo",
            "CD",
            "COD",
        ),
        (
            "Cook Islands",
            "CK",
            "COK",
        ),
        (
            "Costa Rica",
            "CR",
            "CRI",
        ),
        (
            "Ivory Coast",
            "CI",
            "CIV",
        ),
        (
            "Croatia",
            "HR",
            "HRV",
        ),
        (
            "Cuba",
            "CU",
            "CUB",
        ),
        (
            "Cyprus",
            "CY",
            "CYP",
        ),
        (
            "Czech Republic",
            "CZ",
            "CZE",
        ),
        (
            "Denmark",
            "DK",
            "DNK",
        ),
        (
            "Djibouti",
            "DJ",
            "DJI",
        ),
        (
            "Dominica",
            "DM",
            "DMA",
        ),
        (
            "Dominican Republic",
            "DO",
            "DOM",
        ),
        (
            "Ecuador",
            "EC",
            "ECU",
        ),
        (
            "Egypt",
            "EG",
            "EGY",
        ),
        (
            "El Salvador",
            "SV",
            "SLV",
        ),
        (
            "Equatorial Guinea",
            "GQ",
            "GNQ",
        ),
        (
            "Eritrea",
            "ER",
            "ERI",
        ),
        (
            "Estonia",
            "EE",
            "EST",
        ),
        (
            "Ethiopia",
            "ET",
            "ETH",
        ),
        (
            "Falkland Islands (Malvinas)",
            "FK",
            "FLK",
        ),
        (
            "Faroe Islands",
            "FO",
            "FRO",
        ),
        (
            "Fiji",
            "FJ",
            "FJI",
        ),
        (
            "Finland",
            "FI",
            "FIN",
        ),
        (
            "France",
            "FR",
            "FRA",
        ),
        (
            "French Guiana",
            "GF",
            "GUF",
        ),
        (
            "French Polynesia",
            "PF",
            "PYF",
        ),
        (
            "French Southern Territories",
            "TF",
            "ATF",
        ),
        (
            "Gabon",
            "GA",
            "GAB",
        ),
        (
            "Gambia",
            "GM",
            "GMB",
        ),
        (
            "Georgia",
            "GE",
            "GEO",
        ),
        (
            "Germany",
            "DE",
            "DEU",
        ),
        (
            "Ghana",
            "GH",
            "GHA",
        ),
        (
            "Gibraltar",
            "GI",
            "GIB",
        ),
        (
            "Greece",
            "GR",
            "GRC",
        ),
        (
            "Greenland",
            "GL",
            "GRL",
        ),
        (
            "Grenada",
            "GD",
            "GRD",
        ),
        (
            "Guadeloupe",
            "GP",
            "GLP",
        ),
        (
            "Guam",
            "GU",
            "GUM",
        ),
        (
            "Guatemala",
            "GT",
            "GTM",
        ),
        (
            "Guernsey",
            "GG",
            "GGY",
        ),
        (
            "Guinea",
            "GN",
            "GIN",
        ),
        (
            "Guinea-Bissau",
            "GW",
            "GNB",
        ),
        (
            "Guyana",
            "GY",
            "GUY",
        ),
        (
            "Haiti",
            "HT",
            "HTI",
        ),
        (
            "Heard Island and McDonald Islands",
            "HM",
            "HMD",
        ),
        (
            "Holy See (Vatican City State)",
            "VA",
            "VAT",
        ),
        (
            "Honduras",
            "HN",
            "HND",
        ),
        (
            "Hong Kong",
            "HK",
            "HKG",
        ),
        (
            "Hungary",
            "HU",
            "HUN",
        ),
        (
            "Iceland",
            "IS",
            "ISL",
        ),
        (
            "India",
            "IN",
            "IND",
        ),
        (
            "Indonesia",
            "ID",
            "IDN",
        ),
        (
            "Iran, Islamic Republic of",
            "IR",
            "IRN",
        ),
        (
            "Iraq",
            "IQ",
            "IRQ",
        ),
        (
            "Ireland",
            "IE",
            "IRL",
        ),
        (
            "Isle of Man",
            "IM",
            "IMN",
        ),
        (
            "Israel",
            "IL",
            "ISR",
        ),
        (
            "Italy",
            "IT",
            "ITA",
        ),
        (
            "Jamaica",
            "JM",
            "JAM",
        ),
        (
            "Japan",
            "JP",
            "JPN",
        ),
        (
            "Jersey",
            "JE",
            "JEY",
        ),
        (
            "Jordan",
            "JO",
            "JOR",
        ),
        (
            "Kazakhstan",
            "KZ",
            "KAZ",
        ),
        (
            "Kenya",
            "KE",
            "KEN",
        ),
        (
            "Kiribati",
            "KI",
            "KIR",
        ),
        (
            "Democratic People's Republic of Korea",
            "KP",
            "PRK",
        ),
        (
            "South Korea",
            "KR",
            "KOR",
        ),
        (
            "Kuwait",
            "KW",
            "KWT",
        ),
        (
            "Kyrgyzstan",
            "KG",
            "KGZ",
        ),
        (
            "Lao People's Democratic Republic",
            "LA",
            "LAO",
        ),
        (
            "Latvia",
            "LV",
            "LVA",
        ),
        (
            "Lebanon",
            "LB",
            "LBN",
        ),
        (
            "Lesotho",
            "LS",
            "LSO",
        ),
        (
            "Liberia",
            "LR",
            "LBR",
        ),
        (
            "Libya",
            "LY",
            "LBY",
        ),
        (
            "Liechtenstein",
            "LI",
            "LIE",
        ),
        (
            "Lithuania",
            "LT",
            "LTU",
        ),
        (
            "Luxembourg",
            "LU",
            "LUX",
        ),
        (
            "Macao",
            "MO",
            "MAC",
        ),
        (
            "Republic of North Macedonia",
            "MK",
            "MKD",
        ),
        (
            "Madagascar",
            "MG",
            "MDG",
        ),
        (
            "Malawi",
            "MW",
            "MWI",
        ),
        (
            "Malaysia",
            "MY",
            "MYS",
        ),
        (
            "Maldives",
            "MV",
            "MDV",
        ),
        (
            "Mali",
            "ML",
            "MLI",
        ),
        (
            "Malta",
            "MT",
            "MLT",
        ),
        (
            "Marshall Islands",
            "MH",
            "MHL",
        ),
        (
            "Martinique",
            "MQ",
            "MTQ",
        ),
        (
            "Mauritania",
            "MR",
            "MRT",
        ),
        (
            "Mauritius",
            "MU",
            "MUS",
        ),
        (
            "Mayotte",
            "YT",
            "MYT",
        ),
        (
            "Mexico",
            "MX",
            "MEX",
        ),
        (
            "Federated States of Micronesia",
            "FM",
            "FSM",
        ),
        (
            "Republic of Moldova",
            "MD",
            "MDA",
        ),
        (
            "Monaco",
            "MC",
            "MCO",
        ),
        (
            "Mongolia",
            "MN",
            "MNG",
        ),
        (
            "Montenegro",
            "ME",
            "MNE",
        ),
        (
            "Montserrat",
            "MS",
            "MSR",
        ),
        (
            "Morocco",
            "MA",
            "MAR",
        ),
        (
            "Mozambique",
            "MZ",
            "MOZ",
        ),
        (
            "Myanmar",
            "MM",
            "MMR",
        ),
        (
            "Namibia",
            "NA",
            "NAM",
        ),
        (
            "Nauru",
            "NR",
            "NRU",
        ),
        (
            "Nepal",
            "NP",
            "NPL",
        ),
        (
            "Netherlands",
            "NL",
            "NLD",
        ),
        (
            "Netherlands Antilles",
            "AN",
            "ANT",
        ),
        (
            "New Caledonia",
            "NC",
            "NCL",
        ),
        (
            "New Zealand",
            "NZ",
            "NZL",
        ),
        (
            "Nicaragua",
            "NI",
            "NIC",
        ),
        (
            "Niger",
            "NE",
            "NER",
        ),
        (
            "Nigeria",
            "NG",
            "NGA",
        ),
        (
            "Niue",
            "NU",
            "NIU",
        ),
        (
            "Norfolk Island",
            "NF",
            "NFK",
        ),
        (
            "Northern Mariana Islands",
            "MP",
            "MNP",
        ),
        (
            "Norway",
            "NO",
            "NOR",
        ),
        (
            "Oman",
            "OM",
            "OMN",
        ),
        (
            "Pakistan",
            "PK",
            "PAK",
        ),
        (
            "Palau",
            "PW",
            "PLW",
        ),
        (
            "Palestinian Territory, Occupied",
            "PS",
            "PSE",
        ),
        (
            "Panama",
            "PA",
            "PAN",
        ),
        (
            "Papua New Guinea",
            "PG",
            "PNG",
        ),
        (
            "Paraguay",
            "PY",
            "PRY",
        ),
        (
            "Peru",
            "PE",
            "PER",
        ),
        (
            "Philippines",
            "PH",
            "PHL",
        ),
        (
            "Pitcairn",
            "PN",
            "PCN",
        ),
        (
            "Poland",
            "PL",
            "POL",
        ),
        (
            "Portugal",
            "PT",
            "PRT",
        ),
        (
            "Puerto Rico",
            "PR",
            "PRI",
        ),
        (
            "Qatar",
            "QA",
            "QAT",
        ),
        (
            "Réunion",
            "RE",
            "REU",
        ),
        (
            "Romania",
            "RO",
            "ROU",
        ),
        (
            "Russia",
            "RU",
            "RUS",
        ),
        (
            "Rwanda",
            "RW",
            "RWA",
        ),
        (
            "Saint Helena, Ascension and Tristan da Cunha",
            "SH",
            "SHN",
        ),
        (
            "Saint Kitts and Nevis",
            "KN",
            "KNA",
        ),
        (
            "Saint Lucia",
            "LC",
            "LCA",
        ),
        (
            "Saint Pierre and Miquelon",
            "PM",
            "SPM",
        ),
        (
            "Saint Vincent and the Grenadines",
            "VC",
            "VCT",
        ),
        (
            "Samoa",
            "WS",
            "WSM",
        ),
        (
            "San Marino",
            "SM",
            "SMR",
        ),
        (
            "Sao Tome and Principe",
            "ST",
            "STP",
        ),
        (
            "Saudi Arabia",
            "SA",
            "SAU",
        ),
        (
            "Senegal",
            "SN",
            "SEN",
        ),
        (
            "Serbia",
            "RS",
            "SRB",
        ),
        (
            "Seychelles",
            "SC",
            "SYC",
        ),
        (
            "Sierra Leone",
            "SL",
            "SLE",
        ),
        (
            "Singapore",
            "SG",
            "SGP",
        ),
        (
            "Slovakia",
            "SK",
            "SVK",
        ),
        (
            "Slovenia",
            "SI",
            "SVN",
        ),
        (
            "Solomon Islands",
            "SB",
            "SLB",
        ),
        (
            "Somalia",
            "SO",
            "SOM",
        ),
        (
            "South Africa",
            "ZA",
            "ZAF",
        ),
        (
            "South Georgia and the South Sandwich Islands",
            "GS",
            "SGS",
        ),
        (
            "South Sudan",
            "SS",
            "SSD",
        ),
        (
            "Spain",
            "ES",
            "ESP",
        ),
        (
            "Sri Lanka",
            "LK",
            "LKA",
        ),
        (
            "Sudan",
            "SD",
            "SDN",
        ),
        (
            "Suriname",
            "SR",
            "SUR",
        ),
        (
            "Svalbard and Jan Mayen",
            "SJ",
            "SJM",
        ),
        (
            "Swaziland",
            "SZ",
            "SWZ",
        ),
        (
            "Sweden",
            "SE",
            "SWE",
        ),
        (
            "Switzerland",
            "CH",
            "CHE",
        ),
        (
            "Syrian Arab Republic",
            "SY",
            "SYR",
        ),
        (
            "Taiwan",
            "TW",
            "TWN",
        ),
        (
            "Tajikistan",
            "TJ",
            "TJK",
        ),
        (
            "Tanzania, United Republic of",
            "TZ",
            "TZA",
        ),
        (
            "Thailand",
            "TH",
            "THA",
        ),
        (
            "Timor-Leste",
            "TL",
            "TLS",
        ),
        (
            "Togo",
            "TG",
            "TGO",
        ),
        (
            "Tokelau",
            "TK",
            "TKL",
        ),
        (
            "Tonga",
            "TO",
            "TON",
        ),
        (
            "Trinidad and Tobago",
            "TT",
            "TTO",
        ),
        (
            "Tunisia",
            "TN",
            "TUN",
        ),
        (
            "Turkey",
            "TR",
            "TUR",
        ),
        (
            "Turkmenistan",
            "TM",
            "TKM",
        ),
        (
            "Turks and Caicos Islands",
            "TC",
            "TCA",
        ),
        (
            "Tuvalu",
            "TV",
            "TUV",
        ),
        (
            "Uganda",
            "UG",
            "UGA",
        ),
        (
            "Ukraine",
            "UA",
            "UKR",
        ),
        (
            "United Arab Emirates",
            "AE",
            "ARE",
        ),
        (
            "United Kingdom",
            "GB",
            "GBR",
        ),
        (
            "United States",
            "US",
            "USA",
        ),
        (
            "United States Minor Outlying Islands",
            "UM",
            "UMI",
        ),
        (
            "Uruguay",
            "UY",
            "URY",
        ),
        (
            "Uzbekistan",
            "UZ",
            "UZB",
        ),
        (
            "Vanuatu",
            "VU",
            "VUT",
        ),
        (
            "Venezuela",
            "VE",
            "VEN",
        ),
        (
            "Vietnam",
            "VN",
            "VNM",
        ),
        (
            "Virgin Islands, British",
            "VG",
            "VGB",
        ),
        (
            "Virgin Islands, U.S.",
            "VI",
            "VIR",
        ),
        (
            "Wallis and Futuna",
            "WF",
            "WLF",
        ),
        (
            "Western Sahara",
            "EH",
            "ESH",
        ),
        (
            "Yemen",
            "YE",
            "YEM",
        ),
        (
            "Zambia",
            "ZM",
            "ZMB",
        ),
        (
            "Zimbabwe",
            "ZW",
            "ZWE",
        ),
    }

    @classmethod
    def get_choices(cls, output_code: str = "alpha2") -> list:
        if output_code not in ("alpha2", "alpha3"):
            logger.warning(f"output_code have to be one of: alpha2, alpha3, provided output_code={output_code}")
            raise ValueError("output_code have to be one of: alpha2, alpha3")
        return [
            {"label": {"English(EN)": name}, "value": alpha2 if output_code == "alpha2" else alpha3}
            for name, alpha2, alpha3 in cls.COUNTRIES
        ]

    @classmethod
    def is_valid_country_choice(cls, choice: str) -> bool:
        return any(choice in CaseInsensitiveTuple(country_tuple) for country_tuple in cls.COUNTRIES)

    @classmethod
    def get_country_value(cls, input_value: str, output_type: str = "alpha2", *args: Any, **kwargs: Any) -> str | None:
        index_map = {
            "name": 0,
            "alpha2": 1,
            "alpha3": 2,
        }

        if output_type not in ("name", "alpha2", "alpha3"):
            logger.warning(f"output_type have to be one of: alpha2, alpha3, provided output_type={output_type}")
            raise ValueError("output_type have to be one of: name, alpha2, alpha3")

        for country_tuple in cls.COUNTRIES:
            if input_value in CaseInsensitiveTuple(country_tuple):
                return country_tuple[index_map[output_type]]

        return None
