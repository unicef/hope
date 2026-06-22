from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

from django.core.validators import validate_image_file_extension
from django.db import models
from django.db.models import (
    JSONField,
    Q,
    QuerySet,
    UniqueConstraint,
)
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField
from sorl.thumbnail import ImageField

from hope.apps.activity_log.utils import create_mapping_dict
from hope.apps.household.const import (
    BLANK,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    STATUS_ACTIVE,
    STATUS_INACTIVE,
    get_data_sharing_choices,
    get_org_enumerator_choices,
    get_registration_method_choices,
    get_residence_status_choices,
)
from hope.apps.household.field_validators import validate_originating_id
from hope.apps.household.mixins import (
    HouseholdDeliveryDataMixin,
)
from hope.apps.household.signals import (
    household_deleted,
    household_withdrawn,
)
from hope.models.storage_file import StorageFile
from hope.models.utils import (
    AbstractSyncable,
    AdminUrlMixin,
    ConcurrencyModel,
    InternalDataFieldModel,
    PendingManager,
    SoftDeletableMergeStatusModel,
    TimeStampedUUIDModel,
    UnicefIdentifiedModel,
)

if TYPE_CHECKING:
    from hope.contrib.aurora.models import Record
    from hope.models.area import Area
    from hope.models.business_area import BusinessArea
    from hope.models.individual import Individual

logger = logging.getLogger(__name__)


class HouseholdCollection(UnicefIdentifiedModel):
    """Collection of household representations."""

    def __str__(self) -> str:
        return self.unicef_id or ""

    @property
    def business_area(self) -> BusinessArea | None:
        return self.households.first().business_area if self.households.first() else None

    class Meta:
        app_label = "household"
        ordering = ("id",)


class Household(
    InternalDataFieldModel,
    SoftDeletableMergeStatusModel,
    TimeStampedUUIDModel,
    AbstractSyncable,
    ConcurrencyModel,
    UnicefIdentifiedModel,
    AdminUrlMixin,
    HouseholdDeliveryDataMixin,
):
    class CollectType(models.TextChoices):
        STANDARD = "STANDARD", "Standard"
        SINGLE = "SINGLE", "Single"

        @staticmethod
        def get_choices() -> list[tuple[str, str]]:
            return Household.CollectType.choices

    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "withdrawn",
            "status",
            "consent_sign",
            "consent",
            "consent_sharing",
            "residence_status",
            "country_origin",
            "country",
            "zip_code",
            "size",
            "address",
            "admin1",
            "admin2",
            "admin3",
            "admin4",
            "representatives",
            "latitude",
            "longitude",
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "pregnant_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
            "female_age_group_0_5_disabled_count",
            "female_age_group_6_11_disabled_count",
            "female_age_group_12_17_disabled_count",
            "female_age_group_18_59_disabled_count",
            "female_age_group_60_disabled_count",
            "male_age_group_0_5_disabled_count",
            "male_age_group_6_11_disabled_count",
            "male_age_group_12_17_disabled_count",
            "male_age_group_18_59_disabled_count",
            "male_age_group_60_disabled_count",
            "other_sex_group_count",
            "unknown_sex_group_count",
            "registration_data_import",
            "program",
            "returnee",
            "flex_fields",
            "first_registration_date",
            "last_registration_date",
            "head_of_household",
            "fchild_hoh",
            "child_hoh",
            "unicef_id",
            "start",
            "deviceid",
            "name_enumerator",
            "org_enumerator",
            "org_name_enumerator",
            "village",
            "registration_method",
            "unhcr_id",
            "detail_id",
            "program_registration_id",
            "facility",
        ],
        {
            "currency.code": "currency",
        },
    )
    business_area = models.ForeignKey(
        "core.BusinessArea",
        on_delete=models.CASCADE,
        help_text="Household business area",
    )
    program = models.ForeignKey(
        "program.Program",
        db_index=True,
        on_delete=models.PROTECT,
        related_name="households",
        help_text="Household program",
    )
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="households",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="Household registration data import",
    )
    household_collection = models.ForeignKey(
        HouseholdCollection,
        related_name="households",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Collection of household representations",
    )
    representatives = models.ManyToManyField(
        to="household.Individual",
        through="household.IndividualRoleInHousehold",
        help_text="""This is only used to track collector (primary or secondary) of a household.
                    They may still be a HOH of this household or any other household.
                    Through model will contain the role (ROLE_CHOICE) they are connected with on.""",
        related_name="represented_households",
    )
    storage_obj = models.ForeignKey(
        StorageFile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Household storage object",
    )
    copied_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="copied_to",
        help_text="If this household was copied from another household, "
        "this field will contain the household it was copied from.",
    )
    country_origin = models.ForeignKey(
        "geo.Country",
        related_name="+",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text="Household country origin",
    )
    country = models.ForeignKey(
        "geo.Country",
        related_name="+",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text="Household country",
    )
    admin1 = models.ForeignKey(
        "geo.Area",
        null=True,
        on_delete=models.PROTECT,
        blank=True,
        related_name="+",
        help_text="Household administrative area level 1",
    )
    admin2 = models.ForeignKey(
        "geo.Area",
        null=True,
        on_delete=models.PROTECT,
        blank=True,
        related_name="+",
        help_text="Household administrative area level 2",
    )
    admin3 = models.ForeignKey(
        "geo.Area",
        null=True,
        on_delete=models.PROTECT,
        blank=True,
        related_name="+",
        help_text="Household administrative area level 3",
    )
    admin4 = models.ForeignKey(
        "geo.Area",
        null=True,
        on_delete=models.PROTECT,
        blank=True,
        related_name="+",
        help_text="Household administrative area level 4",
    )
    head_of_household = models.OneToOneField(
        "Individual",
        related_name="heading_household",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Household head of household",
    )
    facility = models.ForeignKey(
        "Facility",
        related_name="households",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    consent_sign = ImageField(
        validators=[validate_image_file_extension],
        blank=True,
        help_text="Household consent sign image",
    )
    consent = models.BooleanField(null=True, blank=True, help_text="Household consent")
    consent_sharing = MultiSelectField(
        choices=get_data_sharing_choices,
        default=BLANK,
        blank=True,
        help_text="Household consent sharing",
    )
    residence_status = models.CharField(
        max_length=254,
        choices=get_residence_status_choices,
        blank=True,
        help_text="Household residence status",
    )

    address = models.CharField(max_length=1024, blank=True, help_text="Household address", db_collation="und-ci-det")
    zip_code = models.CharField(max_length=12, blank=True, null=True, help_text="Household zip code")

    size = models.PositiveIntegerField(db_index=True, null=True, blank=True, help_text="Household size")
    female_age_group_0_5_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household female age group 0-5"
    )
    female_age_group_6_11_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household female age group 6-11"
    )
    female_age_group_12_17_count = models.PositiveIntegerField(
        default=None,
        null=True,
        blank=True,
        help_text="Household female age group 12-17",
    )
    female_age_group_18_59_count = models.PositiveIntegerField(
        default=None,
        null=True,
        blank=True,
        help_text="Household female age group 18-59",
    )
    female_age_group_60_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household female age group 60"
    )
    pregnant_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household pregnant count"
    )
    male_age_group_0_5_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household male age group 0-5"
    )
    male_age_group_6_11_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household male age group 6-11"
    )
    male_age_group_12_17_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household male age group 12-17"
    )
    male_age_group_18_59_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household male age group 18-59"
    )
    male_age_group_60_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household male age group 60"
    )
    female_age_group_0_5_disabled_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household female age group 0-5"
    )
    female_age_group_6_11_disabled_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household female age group 6-11"
    )
    female_age_group_12_17_disabled_count = models.PositiveIntegerField(
        default=None,
        null=True,
        blank=True,
        help_text="Household female age group 12-17",
    )
    female_age_group_18_59_disabled_count = models.PositiveIntegerField(
        default=None,
        null=True,
        blank=True,
        help_text="Household female age group 18-59",
    )
    female_age_group_60_disabled_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household female age group 60"
    )
    male_age_group_0_5_disabled_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household male age group 0-5"
    )
    male_age_group_6_11_disabled_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household male age group 6-1"
    )
    male_age_group_12_17_disabled_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household male age group 12-17"
    )
    male_age_group_18_59_disabled_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household male age group 18-59"
    )
    male_age_group_60_disabled_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household male age group 60"
    )
    children_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household children count"
    )
    male_children_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household male children count"
    )
    female_children_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household female children count"
    )
    children_disabled_count = models.PositiveIntegerField(
        default=None,
        null=True,
        blank=True,
        help_text="Household children disabled count",
    )
    male_children_disabled_count = models.PositiveIntegerField(
        default=None,
        null=True,
        blank=True,
        help_text="Household male children disabled count",
    )
    female_children_disabled_count = models.PositiveIntegerField(
        default=None,
        null=True,
        blank=True,
        help_text="Household female children disabled count",
    )
    other_sex_group_count = models.PositiveIntegerField(
        default=None, null=True, blank=True, help_text="Household other sex group count"
    )  # OTHER
    unknown_sex_group_count = models.PositiveIntegerField(
        default=None,
        null=True,
        blank=True,
        help_text="Household unknown sex group count",
    )  # NOT_COLLECTED

    returnee = models.BooleanField(null=True, blank=True, help_text="Household returnee status")
    fchild_hoh = models.BooleanField(null=True, blank=True, help_text="Female child headed household flag")
    child_hoh = models.BooleanField(null=True, blank=True, help_text="Child headed household flag")
    village = models.CharField(max_length=250, blank=True, default=BLANK, help_text="Household village")
    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="households",
        help_text="Household currency",
    )
    unhcr_id = models.CharField(
        max_length=250,
        blank=True,
        default=BLANK,
        db_index=True,
        help_text="Household unhcr id",
    )
    # TODO: detail_id is deprecated, will be removed soon. It was replaced with originating_id
    detail_id = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Kobo asset ID, Xlsx row ID, Aurora registration ID",
    )
    originating_id = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        validators=[validate_originating_id],
        help_text="""A unified external reference with a fixed-length source prefix (XLS, KOB, or AUR)
                     and a source-specific identifier separated by '#', e.g., 'KOB#321#123'.""",
    )
    start = models.DateTimeField(blank=True, null=True, help_text="Data collection start date")

    # System fields
    registration_method = models.CharField(
        max_length=250,
        choices=get_registration_method_choices,
        default=BLANK,
        blank=True,
        help_text="Household registration method [sys]",
    )
    family_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Family ID eDopomoga household id [sys]",
    )
    origin_unicef_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Household origin unicef id [sys]",
    )
    is_migration_handled = models.BooleanField(default=False, help_text="Household migration status [sys]")
    migrated_at = models.DateTimeField(null=True, blank=True, help_text="Household migrated at [sys]")
    collect_type = models.CharField(
        choices=CollectType.get_choices,
        default=CollectType.STANDARD.value,
        max_length=8,
        blank=True,
        help_text="Household collect type [sys]",
    )
    program_registration_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        unique=True,
        verbose_name=_("Beneficiary Program Registration Id"),
        help_text="Beneficiary Program Registration id [sys]",
        db_collation="und-ci-det",
    )
    total_cash_received_usd = models.DecimalField(
        null=True,
        decimal_places=2,
        max_digits=64,
        blank=True,
        help_text="Household cash received usd [sys]",
    )
    total_cash_received = models.DecimalField(
        null=True,
        decimal_places=2,
        max_digits=64,
        blank=True,
        help_text="Household cash received [sys]",
    )

    flex_fields = JSONField(default=dict, blank=True, help_text="Household flex fields [sys]")
    first_registration_date = models.DateTimeField(help_text="Household first registration date [sys]")
    last_registration_date = models.DateTimeField(help_text="Household last registration date [sys]")
    withdrawn = models.BooleanField(default=False, db_index=True, help_text="Household withdrawn [sys]")
    withdrawn_date = models.DateTimeField(
        null=True, blank=True, db_index=True, help_text="Household withdrawn date [sys]"
    )
    longitude = models.FloatField(blank=True, null=True, help_text="Household longitude [sys]")
    latitude = models.FloatField(blank=True, null=True, help_text="Household latitude [sys]")
    deviceid = models.CharField(max_length=250, blank=True, default=BLANK, help_text="Household deviceid [sys]")
    name_enumerator = models.CharField(
        max_length=250,
        blank=True,
        default=BLANK,
        help_text="Household name enumerator [sys]",
    )
    org_enumerator = models.CharField(
        max_length=250,
        choices=get_org_enumerator_choices,
        default=BLANK,
        blank=True,
        help_text="Household org enumerator [sys]",
    )
    org_name_enumerator = models.CharField(
        max_length=250,
        blank=True,
        default=BLANK,
        help_text="Household org name enumerator [sys]",
    )
    # TODO: kobo_submission_uuid and kobo_submission_time are deprecated, will be removed soon.
    kobo_submission_uuid = models.UUIDField(
        null=True, blank=True, default=None, help_text="Household Kobo submission uuid [sys]"
    )
    kobo_submission_time = models.DateTimeField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Household Kobo submission time [sys]",
    )
    enumerator_rec_id = models.PositiveIntegerField(
        blank=True, null=True, help_text="Household enumerator record [sys]"
    )
    flex_registrations_record_id = models.PositiveIntegerField(
        blank=True, null=True, help_text="Household flex registrations record [sys]"
    )

    extra_rdis = models.ManyToManyField(
        to="registration_data.RegistrationDataImport",
        blank=True,
        related_name="extra_hh_rdis",
        help_text="This relation is filed when collision of Household happens.",
    )
    identification_key = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        db_index=True,
        help_text="Key used to identify Collisions in the system",
    )

    class Meta:
        app_label = "household"
        verbose_name = "Household"
        permissions = (
            ("withdrawn", "Can withdrawn Household"),
            ("sanity_check", "Sanity check Household"),
            ("gdpr_remove", "GDPR remove Household data"),
            ("logical_delete", "Logical delete Household"),
            ("see_linked_objects", "Can see Linked Objects"),
            ("reset_sync_date", "Can reset sync date"),
        )
        ordering = ("id",)

        indexes = [
            models.Index(
                name="hh_prog_cre_active_merged",
                fields=["program", "created_at"],
                condition=Q(is_removed=False, rdi_merge_status="MERGED"),
            ),
            models.Index(
                name="hh_prog_unicef_act_merg_idx",
                fields=["program", "unicef_id"],
                condition=Q(is_removed=False, rdi_merge_status="MERGED"),
            ),
            models.Index(
                name="hh_size_id_idx",
                fields=["size", "id"],
            ),
            models.Index(
                name="hi_prog_ltreg_act_merg_idx",
                fields=["program", "last_registration_date"],
                condition=Q(is_removed=False, rdi_merge_status="MERGED"),
            ),
            models.Index(
                name="idx_hh_prog_rdi_status",
                fields=["program", "rdi_merge_status"],
                condition=Q(is_removed=False),
            ),
        ]
        constraints = [
            UniqueConstraint(
                fields=["unicef_id", "program"],
                condition=Q(is_removed=False),
                name="unique_hh_unicef_id_in_program",
            ),
            UniqueConstraint(
                fields=["identification_key", "program"],
                condition=Q(is_removed=False)
                & Q(identification_key__isnull=False)
                & Q(rdi_merge_status=SoftDeletableMergeStatusModel.MERGED),
                name="identification_key_unique_constraint",
            ),
            UniqueConstraint(
                fields=["originating_id"],
                condition=Q(is_removed=False) & Q(originating_id__isnull=False),
                name="originating_id_hh_unique_constraint",
            ),
        ]

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        household_deleted.send(self.__class__, instance=self)
        return super().delete(*args, **kwargs)

    @property
    def status(self) -> str:
        return STATUS_INACTIVE if self.withdrawn else STATUS_ACTIVE

    def withdraw(self, tag: Any | None = None, notify: bool = True) -> None:
        self.withdrawn = True
        self.withdrawn_date = timezone.now()
        self.internal_data["withdrawn_tag"] = tag
        self.save()
        if notify:
            household_withdrawn.send(sender=self.__class__, instance=self)

    def unwithdraw(self) -> None:
        self.withdrawn = False
        self.withdrawn_date = None
        self.save()

    @property
    def admin_area(self) -> Area | None:
        """Returns the lowest admin area of the household."""
        return self.admin4 or self.admin3 or self.admin2 or self.admin1

    def set_admin_areas(self, new_admin_area: Area | None = None, save: bool = True) -> None:
        """Propagate admin1,2,3,4 based on admin_area parents."""
        admins = ["admin1", "admin2", "admin3", "admin4"]

        if not new_admin_area:
            new_admin_area = self.admin_area
        if not new_admin_area:
            return
        for admin in admins:
            setattr(self, admin, None)

        new_admin_area_level = new_admin_area.area_type.area_level if new_admin_area else 4  # lowest possible level

        for admin_level in reversed(range(1, new_admin_area_level + 1)):
            setattr(self, f"admin{admin_level}", new_admin_area)
            new_admin_area = getattr(new_admin_area, "parent", None)

        if save:
            self.save(update_fields=admins)

    @property
    def sanction_list_possible_match(self) -> bool:
        return self.individuals.filter(sanction_list_possible_match=True).count() > 0

    @property
    def sanction_list_confirmed_match(self) -> bool:
        return self.individuals.filter(sanction_list_confirmed_match=True).count() > 0

    @property
    def active_individuals(self) -> QuerySet:
        return self.individuals.filter(withdrawn=False, duplicate=False)

    @cached_property
    def primary_collector(self) -> "Individual" | None:
        return self.representatives.filter(households_and_roles__role=ROLE_PRIMARY).first()

    @cached_property
    def alternate_collector(self) -> "Individual" | None:
        return self.representatives.filter(households_and_roles__role=ROLE_ALTERNATE).first()

    @property
    def flex_registrations_record(self) -> "Record" | None:
        from hope.contrib.aurora.models import Record

        return Record.objects.filter(id=self.flex_registrations_record_id).first()

    @property
    def geopoint(self) -> str | None:
        if self.latitude and self.longitude:
            return f"{self.latitude},{self.longitude}"
        return None

    @geopoint.setter
    def geopoint(self, value: tuple[float, float] | None) -> None:
        if value:
            (
                self.longitude,
                self.latitude,
            ) = (
                value[0],
                value[1],
            )
        else:
            self.latitude = None
            self.longitude = None

    def __str__(self) -> str:
        return self.unicef_id or ""

    def can_be_erase(self) -> bool:
        yesterday = timezone.now() - timedelta(days=1)
        conditions = [
            self.is_removed,
            self.withdrawn,
            self.removed_date >= yesterday,  # type: ignore[operator]
            self.withdrawn_date >= yesterday,  # type: ignore[operator]
        ]
        return all(conditions)

    def erase(self) -> None:
        for individual in self.individuals.all():
            individual.erase()

        self.flex_fields = {}
        self.save()


class PendingHousehold(Household):
    objects = PendingManager()

    @property
    def individuals(self) -> QuerySet:  # type: ignore[override]
        return super().individuals(manager="pending_objects")  # type: ignore[return-value]

    @property
    def individuals_and_roles(self) -> QuerySet:  # type: ignore[override]
        return super().individuals_and_roles(manager="pending_objects")  # type: ignore[return-value]

    @property
    def pending_representatives(self) -> QuerySet:
        return super().representatives(manager="pending_objects")  # type: ignore[return-value]

    @cached_property
    def primary_collector(self) -> "Individual" | None:
        return self.pending_representatives.get(households_and_roles__role=ROLE_PRIMARY)

    @cached_property
    def alternate_collector(self) -> "Individual" | None:
        return self.pending_representatives.filter(households_and_roles__role=ROLE_ALTERNATE).first()

    class Meta:
        app_label = "household"
        proxy = True
        verbose_name = "Imported Household"
        verbose_name_plural = "Imported Households"
