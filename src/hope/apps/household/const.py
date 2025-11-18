from django.utils.translation import gettext_lazy as _
from django_countries.data import COUNTRIES

NATIONALITIES = (
    ("AF", _("Afghan")),
    ("AL", _("Albanian")),
    ("DZ", _("Algerian")),
    ("AD", _("Andorran")),
    ("AO", _("Angolan")),
    ("AR", _("Argentinian")),
    ("AM", _("Armenian")),
    ("A", _("Australian")),
    ("AT", _("Austrian")),
    ("AZ", _("Azerbaijani")),
    ("BS", _("Bahamian")),
    ("BH", _("Bahraini")),
    ("BD", _("Bangladeshi")),
    ("BB", _("Barbadian")),
    ("BY", _("Belorussian")),
    ("BE", _("Belgian")),
    ("BZ", _("Belizian")),
    ("BJ", _("Beninese")),
    ("BT", _("Bhutanese")),
    ("BO", _("Bolivian")),
    ("BA", _("Bosnian")),
    ("BW", _("Botswanan")),
    ("BR", _("Brazilian")),
    ("GB", _("British")),
    ("BN", _("Bruneian")),
    ("BG", _("Bulgarian")),
    ("BF", _("Burkinese")),
    ("MM", _("Burmese")),
    ("BF", _("Burundian")),
    ("BI", _("Cambodian")),
    ("CM", _("Cameroonian")),
    ("CA", _("Canadian")),
    ("CV", _("Cape Verdean")),
    ("TD", _("Chadian")),
    ("CL", _("Chilean")),
    ("CN", _("Chinese")),
    ("CO", _("Colombian")),
    ("CG", _("Congolese")),
    ("CR", _("Costa Rican")),
    ("HR", _("Croatian")),
    ("C", _("Cuban")),
    ("CY", _("Cypriot")),
    ("CZ", _("Czech")),
    ("DK", _("Danish")),
    ("DJ", _("Djiboutian")),
    ("DM", _("Dominican")),
    ("DO", _("Dominican")),
    ("EC", _("Ecuadorean")),
    ("EG", _("Egyptian")),
    ("SV", _("Salvadorean")),
    ("GB", _("English")),
    ("ER", _("Eritrean")),
    ("EE", _("Estonian")),
    ("ET", _("Ethiopian")),
    ("FJ", _("Fijian")),
    ("FI", _("Finnish")),
    ("FR", _("French")),
    ("GA", _("Gabonese")),
    ("GM", _("Gambian")),
    ("GE", _("Georgian")),
    ("DE", _("German")),
    ("GH", _("Ghanaian")),
    ("GR", _("Greek")),
    ("GD", _("Grenadian")),
    ("GT", _("Guatemalan")),
    ("GQ", _("Guinean")),
    ("GY", _("Guyanese")),
    ("HT", _("Haitian")),
    ("NL", _("Dutch")),
    ("HN", _("Honduran")),
    ("H", _("Hungarian")),
    ("IS", _("Icelandic")),
    ("IO", _("Indian")),
    ("ID", _("Indonesian")),
    ("IR", _("Iranian")),
    ("IQ", _("Iraqi")),
    ("IE", _("Irish")),
    ("IL", _("Israeli")),
    ("IT", _("Italian")),
    ("JM", _("Jamaican")),
    ("JP", _("Japanese")),
    ("JO", _("Jordanian")),
    ("KZ", _("Kazakh")),
    ("KE", _("Kenyan")),
    ("KW", _("Kuwaiti")),
    ("LA", _("Laotian")),
    ("LV", _("Latvian")),
    ("LB", _("Lebanese")),
    ("LR", _("Liberian")),
    ("LY", _("Libyan")),
    ("LT", _("Lithuanian")),
    ("MK", _("Macedonian")),
    ("MG", _("Malagasay")),
    ("MW", _("Malawian")),
    ("MY", _("Malaysian")),
    ("MV", _("Maldivian")),
    ("ML", _("Malian")),
    ("MT", _("Maltese")),
    ("MR", _("Mauritanian")),
    ("M", _("Mauritian")),
    ("MX", _("Mexican")),
    ("MD", _("Moldovan")),
    ("MC", _("Monacan")),
    ("MN", _("Mongolian")),
    ("ME", _("Montenegrin")),
    ("MA", _("Moroccan")),
    ("MZ", _("Mozambican")),
    ("NA", _("Namibian")),
    ("NP", _("Nepalese")),
    ("NI", _("Nicaraguan")),
    ("NE", _("Nigerien")),
    ("NG", _("Nigerian")),
    ("KP", _("North Korean")),
    ("NO", _("Norwegian")),
    ("OM", _("Omani")),
    ("PK", _("Pakistani")),
    ("PA", _("Panamanian")),
    ("PG", _("Guinean")),
    ("PY", _("Paraguayan")),
    ("PE", _("Peruvian")),
    ("PH", _("Philippine")),
    ("PL", _("Polish")),
    ("PT", _("Portuguese")),
    ("QA", _("Qatari")),
    ("RO", _("Romanian")),
    ("R", _("Russian")),
    ("RW", _("Rwandan")),
    ("SA", _("Saudi")),
    ("AE", _("Scottish")),
    ("SN", _("Senegalese")),
    ("RS", _("Serbian")),
    ("SC", _("Seychellois")),
    ("SL", _("Sierra Leonian")),
    ("SG", _("Singaporean")),
    ("SK", _("Slovak")),
    ("SI", _("Slovenian")),
    ("SO", _("Somali")),
    ("ZA", _("South African")),
    ("KR", _("South Korean")),
    ("ES", _("Spanish")),
    ("LK", _("Sri Lankan")),
    ("SD", _("Sudanese")),
    ("SR", _("Surinamese")),
    ("SZ", _("Swazi")),
    ("SE", _("Swedish")),
    ("CH", _("Swiss")),
    ("SY", _("Syrian")),
    ("TW", _("Taiwanese")),
    ("TJ", _("Tadjik")),
    ("TZ", _("Tanzanian")),
    ("TH", _("Thai")),
    ("TG", _("Togolese")),
    ("TT", _("Trinidadian")),
    ("TN", _("Tunisian")),
    ("TR", _("Turkish")),
    ("TM", _("Turkmen")),
    ("TV", _("Tuvaluan")),
    ("UG", _("Ugandan")),
    ("UA", _("Ukrainian")),
    ("UY", _("Uruguayan")),
    ("UZ", _("Uzbek")),
    ("V", _("Vanuatuan")),
    ("VE", _("Venezuelan")),
    ("VN", _("Vietnamese")),
    ("GB", _("Welsh")),
    ("YE", _("Yemeni")),
    ("ZM", _("Zambian")),
    ("ZW", _("Zimbabwean")),
)

COUNTRIES_NAME_ALPHA2 = {str(name): code for code, name in COUNTRIES.items()}

BLANK = ""
IDP = "IDP"
REFUGEE = "REFUGEE"
OTHERS_OF_CONCERN = "OTHERS_OF_CONCERN"
HOST = "HOST"
NON_HOST = "NON_HOST"
RETURNEE = "RETURNEE"
RESIDENCE_STATUS_CHOICE = (
    (BLANK, _("None")),
    (IDP, _("Displaced  |  Internally Displaced People")),
    (REFUGEE, _("Displaced  |  Refugee / Asylum Seeker")),
    (OTHERS_OF_CONCERN, _("Displaced  |  Others of Concern")),
    (HOST, _("Non-displaced  |   Host")),
    (NON_HOST, _("Non-displaced  |   Non-host")),
    (RETURNEE, _("Displaced  |   Returnee")),
)
# INDIVIDUALS
MALE = "MALE"
FEMALE = "FEMALE"
OTHER = "OTHER"
NOT_COLLECTED = "NOT_COLLECTED"
NOT_ANSWERED = "NOT_ANSWERED"

SEX_CHOICE = (
    (MALE, _("Male")),
    (FEMALE, _("Female")),
    (OTHER, _("Other")),
    (NOT_COLLECTED, _("Not collected")),
    (NOT_ANSWERED, _("Not answered")),
)

SINGLE = "SINGLE"
MARRIED = "MARRIED"
WIDOWED = "WIDOWED"
DIVORCED = "DIVORCED"
SEPARATED = "SEPARATED"
MARITAL_STATUS_CHOICE = (
    (BLANK, _("None")),
    (DIVORCED, _("Divorced")),
    (MARRIED, _("Married")),
    (SEPARATED, _("Separated")),
    (SINGLE, _("Single")),
    (WIDOWED, _("Widowed")),
)

NONE = "NONE"
SEEING = "SEEING"
HEARING = "HEARING"
WALKING = "WALKING"
MEMORY = "MEMORY"
SELF_CARE = "SELF_CARE"
COMMUNICATING = "COMMUNICATING"
OBSERVED_DISABILITY_CHOICE = (
    (NONE, _("None")),
    (SEEING, _("Difficulty seeing (even if wearing glasses)")),
    (HEARING, _("Difficulty hearing (even if using a hearing aid)")),
    (WALKING, _("Difficulty walking or climbing steps")),
    (MEMORY, _("Difficulty remembering or concentrating")),
    (SELF_CARE, _("Difficulty with self care (washing, dressing)")),
    (
        COMMUNICATING,
        _("Difficulty communicating (e.g understanding or being understood)"),
    ),
)
NON_BENEFICIARY = "NON_BENEFICIARY"  # delegate
HEAD = "HEAD"
SON_DAUGHTER = "SON_DAUGHTER"
WIFE_HUSBAND = "WIFE_HUSBAND"
BROTHER_SISTER = "BROTHER_SISTER"
MOTHER_FATHER = "MOTHER_FATHER"
AUNT_UNCLE = "AUNT_UNCLE"
GRANDMOTHER_GRANDFATHER = "GRANDMOTHER_GRANDFATHER"
MOTHERINLAW_FATHERINLAW = "MOTHERINLAW_FATHERINLAW"
DAUGHTERINLAW_SONINLAW = "DAUGHTERINLAW_SONINLAW"
SISTERINLAW_BROTHERINLAW = "SISTERINLAW_BROTHERINLAW"
GRANDDAUGHTER_GRANDSON = "GRANDDAUGHER_GRANDSON"  # key is wrong, but it is used in kobo and aurora
NEPHEW_NIECE = "NEPHEW_NIECE"
COUSIN = "COUSIN"
FOSTER_CHILD = "FOSTER_CHILD"
RELATIONSHIP_UNKNOWN = "UNKNOWN"
RELATIONSHIP_OTHER = "OTHER"
FREE_UNION = "FREE_UNION"

RELATIONSHIP_CHOICE = (
    (RELATIONSHIP_UNKNOWN, "Unknown"),
    (AUNT_UNCLE, "Aunt / Uncle"),
    (BROTHER_SISTER, "Brother / Sister"),
    (COUSIN, "Cousin"),
    (DAUGHTERINLAW_SONINLAW, "Daughter-in-law / Son-in-law"),
    (GRANDDAUGHTER_GRANDSON, "Granddaughter / Grandson"),
    (GRANDMOTHER_GRANDFATHER, "Grandmother / Grandfather"),
    (HEAD, "Head of household (self)"),
    (MOTHER_FATHER, "Mother / Father"),
    (MOTHERINLAW_FATHERINLAW, "Mother-in-law / Father-in-law"),
    (NEPHEW_NIECE, "Nephew / Niece"),
    (
        NON_BENEFICIARY,
        "Not a Family Member. Can only act as a recipient.",
    ),
    (RELATIONSHIP_OTHER, "Other"),
    (SISTERINLAW_BROTHERINLAW, "Sister-in-law / Brother-in-law"),
    (SON_DAUGHTER, "Son / Daughter"),
    (WIFE_HUSBAND, "Wife / Husband"),
    (FOSTER_CHILD, "Foster child"),
    (FREE_UNION, "Free union"),
)
YES = "1"
NO = "0"
YES_NO_CHOICE = (
    (BLANK, _("None")),
    (YES, _("Yes")),
    (NO, _("No")),
)

NOT_PROVIDED = "NOT_PROVIDED"
WORK_STATUS_CHOICE = (
    (YES, _("Yes")),
    (NO, _("No")),
    (NOT_PROVIDED, _("Not provided")),
)
ROLE_PRIMARY = "PRIMARY"
ROLE_ALTERNATE = "ALTERNATE"
ROLE_CHOICE = (
    (ROLE_ALTERNATE, "Alternate collector"),
    (ROLE_PRIMARY, "Primary collector"),
)
IDENTIFICATION_TYPE_BIRTH_CERTIFICATE = "BIRTH_CERTIFICATE"
IDENTIFICATION_TYPE_DRIVERS_LICENSE = "DRIVERS_LICENSE"
IDENTIFICATION_TYPE_NATIONAL_ID = "NATIONAL_ID"
IDENTIFICATION_TYPE_NATIONAL_PASSPORT = "NATIONAL_PASSPORT"
IDENTIFICATION_TYPE_ELECTORAL_CARD = "ELECTORAL_CARD"
IDENTIFICATION_TYPE_TAX_ID = "TAX_ID"
IDENTIFICATION_TYPE_RESIDENCE_PERMIT_NO = "RESIDENCE_PERMIT_NO"
IDENTIFICATION_TYPE_BANK_STATEMENT = "BANK_STATEMENT"
IDENTIFICATION_TYPE_DISABILITY_CERTIFICATE = "DISABILITY_CERTIFICATE"
IDENTIFICATION_TYPE_FOSTER_CHILD = "FOSTER_CHILD"
IDENTIFICATION_TYPE_OTHER = "OTHER"
IDENTIFICATION_TYPE_CHOICE = (
    (IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, _("Birth Certificate")),
    (IDENTIFICATION_TYPE_DRIVERS_LICENSE, _("Driver's License")),
    (IDENTIFICATION_TYPE_ELECTORAL_CARD, _("Electoral Card")),
    (IDENTIFICATION_TYPE_NATIONAL_ID, _("National ID")),
    (IDENTIFICATION_TYPE_NATIONAL_PASSPORT, _("National Passport")),
    (IDENTIFICATION_TYPE_TAX_ID, _("Tax Number Identification")),
    (IDENTIFICATION_TYPE_RESIDENCE_PERMIT_NO, _("Foreigner's Residence Permit")),
    (IDENTIFICATION_TYPE_BANK_STATEMENT, _("Bank Statement")),
    (IDENTIFICATION_TYPE_DISABILITY_CERTIFICATE, _("Disability Certificate")),
    (IDENTIFICATION_TYPE_FOSTER_CHILD, _("Foster Child")),
    (IDENTIFICATION_TYPE_OTHER, _("Other")),
)
IDENTIFICATION_TYPE_DICT = {
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE: "Birth Certificate",
    IDENTIFICATION_TYPE_DRIVERS_LICENSE: "Driver's License",
    IDENTIFICATION_TYPE_ELECTORAL_CARD: "Electoral Card",
    IDENTIFICATION_TYPE_NATIONAL_ID: "National ID",
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT: "National Passport",
    IDENTIFICATION_TYPE_TAX_ID: "Tax Number Identification",
    IDENTIFICATION_TYPE_RESIDENCE_PERMIT_NO: "Foreigner's Residence Permit",
    IDENTIFICATION_TYPE_OTHER: "Other",
}
UNHCR = "UNHCR"
WFP = "WFP"
AGENCY_TYPE_CHOICES = (
    (UNHCR, _("UNHCR")),
    (WFP, _("WFP")),
)
STATUS_ACTIVE = "ACTIVE"
STATUS_INACTIVE = "INACTIVE"
STATUS_WITHDRAWN = "WITHDRAWN"
STATUS_DUPLICATE = "DUPLICATE"
INDIVIDUAL_STATUS_CHOICES = (
    (STATUS_ACTIVE, "Active"),
    (STATUS_DUPLICATE, "Duplicate"),
    (STATUS_WITHDRAWN, "Withdrawn"),
)
INDIVIDUAL_HOUSEHOLD_STATUS = ((STATUS_ACTIVE, "Active"), (STATUS_INACTIVE, "Inactive"))
UNIQUE = "UNIQUE"
DUPLICATE = "DUPLICATE"
NEEDS_ADJUDICATION = "NEEDS_ADJUDICATION"
NOT_PROCESSED = "NOT_PROCESSED"
DEDUPLICATION_POSTPONE = "POSTPONE"
DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE = (
    (DUPLICATE, "Duplicate"),
    (NEEDS_ADJUDICATION, "Needs Adjudication"),
    (NOT_PROCESSED, "Not Processed"),
    (DEDUPLICATION_POSTPONE, "Postpone"),
    (UNIQUE, "Unique"),
)
SIMILAR_IN_BATCH = "SIMILAR_IN_BATCH"
DUPLICATE_IN_BATCH = "DUPLICATE_IN_BATCH"
UNIQUE_IN_BATCH = "UNIQUE_IN_BATCH"
NOT_PROCESSED = "NOT_PROCESSED"
DEDUPLICATION_BATCH_STATUS_CHOICE = (
    (DUPLICATE_IN_BATCH, "Duplicate in batch"),
    (NOT_PROCESSED, "Not Processed"),
    (SIMILAR_IN_BATCH, "Similar in batch"),
    (UNIQUE_IN_BATCH, "Unique in batch"),
)
SOME_DIFFICULTY = "SOME_DIFFICULTY"
LOT_DIFFICULTY = "LOT_DIFFICULTY"
CANNOT_DO = "CANNOT_DO"
SEVERITY_OF_DISABILITY_CHOICES = (
    (BLANK, _("None")),
    (LOT_DIFFICULTY, "A lot of difficulty"),
    (CANNOT_DO, "Cannot do at all"),
    (SOME_DIFFICULTY, "Some difficulty"),
)
UNICEF = "UNICEF"
PARTNER = "PARTNER"
ORG_ENUMERATOR_CHOICES = (
    (BLANK, _("None")),
    (PARTNER, "Partner"),
    (UNICEF, "UNICEF"),
)
HUMANITARIAN_PARTNER = "HUMANITARIAN_PARTNER"
PRIVATE_PARTNER = "PRIVATE_PARTNER"
GOVERNMENT_PARTNER = "GOVERNMENT_PARTNER"
DATA_SHARING_CHOICES = (
    (BLANK, _("None")),
    (GOVERNMENT_PARTNER, "Government partners"),
    (HUMANITARIAN_PARTNER, "Humanitarian partners"),
    (PRIVATE_PARTNER, "Private partners"),
    (UNICEF, "UNICEF"),
)
HH_REGISTRATION = "HH_REGISTRATION"
COMMUNITY = "COMMUNITY"
REGISTRATION_METHOD_CHOICES = (
    (BLANK, _("None")),
    (COMMUNITY, "Community-level Registration"),
    (HH_REGISTRATION, "Household Registration"),
)

DISABLED = "disabled"
NOT_DISABLED = "not disabled"
DISABILITY_CHOICES = (
    (
        DISABLED,
        "disabled",
    ),
    (
        NOT_DISABLED,
        "not disabled",
    ),
)
SANCTION_LIST_POSSIBLE_MATCH = "SANCTION_LIST_POSSIBLE_MATCH"
SANCTION_LIST_CONFIRMED_MATCH = "SANCTION_LIST_CONFIRMED_MATCH"
INDIVIDUAL_FLAGS_CHOICES = (
    (DUPLICATE, "Duplicate"),
    (NEEDS_ADJUDICATION, "Needs adjudication"),
    (SANCTION_LIST_CONFIRMED_MATCH, "Sanction list match"),
    (SANCTION_LIST_POSSIBLE_MATCH, "Sanction list possible match"),
)
