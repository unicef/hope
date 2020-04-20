from datetime import date

from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
from django.core.validators import (
    validate_image_file_extension,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField

from household.const import NATIONALITIES
from utils.models import TimeStampedUUIDModel


# HOUSEHOLDS
ADMIN1_CHOICE = (
    ("SO11", "Awdal - SO11"),
    ("SO25", "Bakool - SO25"),
    ("SO22", "Banadir - SO22"),
    ("SO16", "Bari - SO16"),
    ("SO24", "Bay - SO24"),
    ("SO19", "Galgaduud - SO19"),
    ("SO26", "Gedo - SO26"),
    ("SO20", "Hiraan - SO20"),
    ("SO27", "Middle Juba - SO27"),
    ("SO28", "Lower Juba - SO28"),
    ("SO18", "Mudug - SO18"),
    ("SO17", "Nugaal - SO17"),
    ("SO15", "Sanaag - SO15"),
    ("SO21", "Middle Shabelle - SO21"),
    ("SO23", "Lower Shabelle - SO23"),
    ("SO14", "Sool - SO14"),
    ("SO13", "Togdheer - SO13"),
    ("SO12", "Woqooyi Galbeed - SO12"),
)
ADMIN2_CHOICE = (
    ("SO2201", "Banadir - SO2201"),
    ("SO1101", "Borama - SO1101"),
    ("SO1102", "Baki - SO1102"),
    ("SO1103", "Lughaye - SO1103"),
    ("SO1104", "Zeylac - SO1104"),
    ("SO1201", "Hargeysa - SO1201"),
    ("SO1202", "Berbera - SO1202"),
    ("SO1203", "Gebiley - SO1203"),
    ("SO1301", "Burco - SO1301"),
    ("SO1302", "Buuhoodle - SO1302"),
    ("SO1303", "Owdweyne - SO1303"),
    ("SO1304", "Sheikh - SO1304"),
    ("SO1401", "Laas Caanood - SO1401"),
    ("SO1402", "Caynabo - SO1402"),
    ("SO1403", "Taleex - SO1403"),
    ("SO1404", "Xudun - SO1404"),
    ("SO1501", "Ceerigaabo - SO1501"),
    ("SO1502", "Ceel Afweyn - SO1502"),
    ("SO1503", "Laasqoray - SO1503"),
    ("SO1601", "Bossaso - SO1601"),
    ("SO1602", "Bandarbeyla - SO1602"),
    ("SO1603", "Caluula - SO1603"),
    ("SO1604", "Iskushuban - SO1604"),
    ("SO1605", "Qandala - SO1605"),
    ("SO1606", "Qardho - SO1606"),
    ("SO1701", "Garoowe - SO1701"),
    ("SO1702", "Burtinle - SO1702"),
    ("SO1703", "Eyl - SO1703"),
    ("SO1801", "Gaalkacyo - SO1801"),
    ("SO1802", "Galdogob - SO1802"),
    ("SO1803", "Hobyo - SO1803"),
    ("SO1804", "Jariiban - SO1804"),
    ("SO1805", "Xarardheere - SO1805"),
    ("SO1901", "Dhuusamarreeb - SO1901"),
    ("SO1902", "Cabudwaaq - SO1902"),
    ("SO1903", "Cadaado - SO1903"),
    ("SO1904", "Ceel Buur - SO1904"),
    ("SO1905", "Ceel Dheer - SO1905"),
    ("SO2001", "Belet Weyne - SO2001"),
    ("SO2002", "Bulo Burto - SO2002"),
    ("SO2003", "Jalalaqsi - SO2003"),
    ("SO2101", "Jowhar - SO2101"),
    ("SO2102", "Adan Yabaal - SO2102"),
    ("SO2103", "Balcad - SO2103"),
    ("SO2104", "Cadale - SO2104"),
    ("SO2301", "Marka - SO2301"),
    ("SO2302", "Afgooye - SO2302"),
    ("SO2303", "Baraawe - SO2303"),
    ("SO2304", "Kurtunwaarey - SO2304"),
    ("SO2305", "Qoryooley - SO2305"),
    ("SO2306", "Sablaale - SO2306"),
    ("SO2307", "Wanla Weyn - SO2307"),
    ("SO2401", "Baydhaba - SO2401"),
    ("SO2402", "Buur Hakaba - SO2402"),
    ("SO2403", "Diinsoor - SO2403"),
    ("SO2404", "Qansax Dheere - SO2404"),
    ("SO2501", "Xudur - SO2501"),
    ("SO2502", "Ceel Barde - SO2502"),
    ("SO2503", "Tayeeglow - SO2503"),
    ("SO2504", "Waajid - SO2504"),
    ("SO2505", "Rab Dhuure - SO2505"),
    ("SO2601", "Garbahaarey - SO2601"),
    ("SO2602", "Baardheere - SO2602"),
    ("SO2603", "Belet Xaawo - SO2603"),
    ("SO2604", "Ceel Waaq - SO2604"),
    ("SO2605", "Doolow - SO2605"),
    ("SO2606", "Luuq - SO2606"),
    ("SO2701", "Bu'aale - SO2701"),
    ("SO2702", "Jilib - SO2702"),
    ("SO2703", "Saakow - SO2703"),
    ("SO2801", "Kismaayo - SO2801"),
    ("SO2802", "Afmadow - SO2802"),
    ("SO2803", "Badhaadhe - SO2803"),
    ("SO2804", "Jamaame - SO2804"),
)
RESIDENCE_STATUS_CHOICE = (
    ("REFUGEE", _("Refugee")),
    ("MIGRANT", _("Migrant")),
    ("CITIZEN", _("Citizen")),
    ("IDP", _("IDP")),
    ("OTHER", _("Other")),
)
# INDIVIDUALS
SEX_CHOICE = (
    ("MALE", _("Male")),
    ("FEMALE", _("Female")),
    ("OTHER", _("Other")),
)
MARTIAL_STATUS_CHOICE = (
    ("SINGLE", _("SINGLE")),
    ("MARRIED", _("Married")),
    ("WIDOW", _("Widow")),
    ("DIVORCED", _("Divorced")),
    ("SEPARATED", _("Separated")),
)
IDENTIFICATION_TYPE_CHOICE = (
    ("NA", _("N/A")),
    ("BIRTH_CERTIFICATE", _("Birth Certificate")),
    ("DRIVING_LICENSE", _("Driving License")),
    ("UNHCR_ID_CARD", _("UNHCR ID card")),
    ("NATIONAL_ID", _("National ID")),
    ("NATIONAL_PASSPORT", _("National Passport")),
)
YES_NO_CHOICE = (
    ("YES", _("Yes")),
    ("NO", _("No")),
)
DISABILITY_CHOICE = (
    ("NO", _("No")),
    ("SEEING", _("Difficulty seeing (even if wearing glasses)")),
    ("HEARING", _("Difficulty hearing (even if using a hearing aid)")),
    ("WALKING", _("Difficulty walking or climbing steps")),
    ("MEMORY", _("Difficulty remembering or concentrating")),
    ("SELF_CARE", _("Difficulty with self care (washing, dressing)")),
    (
        "COMMUNICATING",
        _(
            "Difficulty communicating "
            "(e.g understanding or being understood)"
        ),
    ),
)
RELATIONSHIP_CHOICE = (
    ("NON_BENEFICIARY", "Not a Family Member. Can only act as a recipient.",),
    ("HEAD", "Head of household (self)"),
    ("SON_DAUGHTER", "Son / Daughter"),
    ("WIFE_HUSBAND", "Wife / Husband"),
    ("BROTHER_SISTER", "Brother / Sister"),
    ("MOTHER_FATHER", "Mother / Father"),
    ("AUNT_UNCLE", "Aunt / Uncle"),
    ("GRANDMOTHER_GRANDFATHER", "Grandmother / Grandfather"),
    ("MOTHERINLAW_FATHERINLAW", "Mother-in-law / Father-in-law"),
    ("DAUGHTERINLAW_SONINLAW", "Daughter-in-law / Son-in-law"),
    ("SISTERINLAW_BROTHERINLAW", "Sister-in-law / Brother-in-law"),
    ("GRANDDAUGHER_GRANDSON", "Granddaughter / Grandson"),
    ("NEPHEW_NIECE", "Nephew / Niece"),
    ("COUSIN", "Cousin"),
)
ROLE_CHOICE = (
    ("PRIMARY", "Primary collector"),
    ("ALTERNATE", "Alternate collector"),
    ("NO_ROLE", "None"),
)


class Household(TimeStampedUUIDModel):
    household_ca_id = models.CharField(max_length=255, blank=True)
    consent = ImageField(validators=[validate_image_file_extension])
    residence_status = models.CharField(
        max_length=255, choices=RESIDENCE_STATUS_CHOICE,
    )
    country_origin = models.CharField(max_length=255, choices=NATIONALITIES,)
    size = models.PositiveIntegerField()
    address = models.CharField(max_length=255, blank=True)
    admin1 = models.CharField(
        max_length=255, blank=True, choices=ADMIN1_CHOICE,
    )
    admin2 = models.CharField(
        max_length=255, blank=True, choices=ADMIN2_CHOICE,
    )
    geopoint = PointField(blank=True, null=True)
    unhcr_id = models.CharField(max_length=255, blank=True)
    f_0_5_age_group = models.PositiveIntegerField(default=0)
    f_6_11_age_group = models.PositiveIntegerField(default=0)
    f_12_17_age_group = models.PositiveIntegerField(default=0)
    f_adults = models.PositiveIntegerField(default=0)
    f_pregnant = models.PositiveIntegerField(default=0)
    m_0_5_age_group = models.PositiveIntegerField(default=0)
    m_6_11_age_group = models.PositiveIntegerField(default=0)
    m_12_17_age_group = models.PositiveIntegerField(default=0)
    m_adults = models.PositiveIntegerField(default=0)
    f_0_5_disability = models.PositiveIntegerField(default=0)
    f_6_11_disability = models.PositiveIntegerField(default=0)
    f_12_17_disability = models.PositiveIntegerField(default=0)
    f_adults_disability = models.PositiveIntegerField(default=0)
    m_0_5_disability = models.PositiveIntegerField(default=0)
    m_6_11_disability = models.PositiveIntegerField(default=0)
    m_12_17_disability = models.PositiveIntegerField(default=0)
    m_adults_disability = models.PositiveIntegerField(default=0)
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="households",
        on_delete=models.CASCADE,
    )
    programs = models.ManyToManyField(
        "program.Program", related_name="households", blank=True,
    )
    flex_fields = JSONField(default=dict)
    registration_date = models.DateField(null=True)

    @property
    def total_cash_received(self):
        return (
            self.payment_records.filter()
            .aggregate(Sum("entitlement__delivered_quantity"))
            .get("entitlement__delivered_quantity__sum")
        )

    def __str__(self):
        return f"Household CashAssist ID: {self.household_ca_id}"


class Individual(TimeStampedUUIDModel):
    individual_ca_id = models.CharField(max_length=255, blank=True,)
    individual_id = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    full_name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    given_name = models.CharField(max_length=85, blank=True,)
    middle_name = models.CharField(max_length=85, blank=True,)
    family_name = models.CharField(max_length=85, blank=True,)
    relationship = models.CharField(
        max_length=255, blank=True, choices=RELATIONSHIP_CHOICE,
    )
    role = models.CharField(max_length=255, blank=True, choices=ROLE_CHOICE,)
    sex = models.CharField(max_length=255, choices=SEX_CHOICE,)
    birth_date = models.DateField()
    estimated_birth_date = models.DateField(blank=True, null=True)
    martial_status = models.CharField(
        max_length=255, choices=MARTIAL_STATUS_CHOICE,
    )
    phone_no = PhoneNumberField(blank=True)
    phone_no_alternative = PhoneNumberField(blank=True)
    id_type = models.CharField(
        max_length=255, choices=IDENTIFICATION_TYPE_CHOICE,
    )
    birth_certificate_no = models.CharField(max_length=255, blank=True)
    birth_certificate_photo = models.ImageField(blank=True)
    drivers_license_no = models.CharField(max_length=255, blank=True)
    drivers_license_photo = models.ImageField(blank=True)
    electoral_card_no = models.CharField(max_length=255, blank=True)
    electoral_card_photo = models.ImageField(blank=True)
    unhcr_id_no = models.CharField(max_length=255, blank=True)
    unhcr_id_photo = models.ImageField(blank=True)
    national_passport = models.CharField(max_length=255, blank=True)
    national_passport_photo = models.ImageField(blank=True)
    scope_id_no = models.CharField(max_length=255, blank=True)
    scope_id_photo = models.ImageField(blank=True)
    other_id_type = models.CharField(max_length=255, blank=True)
    other_id_no = models.CharField(max_length=255, blank=True)
    other_id_photo = models.ImageField(blank=True)
    household = models.ForeignKey(
        "Household", related_name="individuals", on_delete=models.CASCADE,
    )
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="individuals",
        on_delete=models.CASCADE,
    )
    work_status = models.CharField(
        max_length=3, default="NO", choices=YES_NO_CHOICE,
    )
    disability = models.CharField(
        max_length=30, default="NO", choices=YES_NO_CHOICE,
    )
    serious_illness = models.CharField(
        max_length=3, choices=YES_NO_CHOICE, blank=True, default="",
    )
    age_first_married = models.PositiveIntegerField(null=True, default=None)
    enrolled_in_school = models.CharField(
        max_length=3, choices=YES_NO_CHOICE, blank=True, default="",
    )
    school_attendance = models.CharField(max_length=100, blank=True, default="")
    school_type = models.CharField(max_length=100, blank=True, default="")
    years_in_school = models.PositiveIntegerField(null=True, default=None)
    minutes_to_school = models.PositiveIntegerField(null=True, default=None)
    enrolled_in_nutrition_programme = models.CharField(
        max_length=3, default="", choices=YES_NO_CHOICE, blank=True,
    )
    administration_of_rutf = models.CharField(
        max_length=3, default="", choices=YES_NO_CHOICE, blank=True,
    )
    flex_fields = JSONField(default=dict)

    @property
    def age(self):
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - (
                (today.month, today.day)
                < (self.birth_date.month, self.birth_date.day)
            )
        )

    def __str__(self):
        return self.full_name


class EntitlementCard(TimeStampedUUIDModel):
    STATUS_CHOICE = Choices(
        ("ACTIVE", _("Active")),
        ("ERRONEOUS", _("Erroneous")),
        ("CLOSED", _("Closed")),
    )
    card_number = models.CharField(max_length=255)
    status = models.CharField(
        choices=STATUS_CHOICE, default=STATUS_CHOICE.ACTIVE, max_length=10,
    )
    card_type = models.CharField(max_length=255)
    current_card_size = models.CharField(max_length=255)
    card_custodian = models.CharField(max_length=255)
    service_provider = models.CharField(max_length=255)
    household = models.ForeignKey(
        "Household",
        related_name="entitlement_cards",
        on_delete=models.SET_NULL,
        null=True,
    )
