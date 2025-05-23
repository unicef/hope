import random
import string
from datetime import date
from decimal import Decimal
from typing import Any, Collection, Optional

from django.conf import settings
from django.contrib.postgres.fields import CICharField
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    MinValueValidator,
    ProhibitNullCharactersValidator,
)
from django.db import models
from django.db.models import Q, QuerySet, Sum
from django.db.models.constraints import UniqueConstraint
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _

from model_utils.models import SoftDeletableModel
from rest_framework.exceptions import ValidationError as DRFValidationError
from strategy_field.fields import StrategyField

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import Payment, PaymentPlan
from hct_mis_api.apps.program.colission_detectors import collision_detectors_registry
from hct_mis_api.apps.utils.models import (
    AbstractSyncable,
    AdminUrlMixin,
    ConcurrencyModel,
    SoftDeletableIsVisibleManager,
    TimeStampedUUIDModel,
    UnicefIdentifiedModel,
)
from hct_mis_api.apps.utils.validators import (
    DoubleSpaceValidator,
    StartEndSpaceValidator,
)


class ProgramPartnerThrough(TimeStampedUUIDModel):
    program = models.ForeignKey(
        "Program",
        on_delete=models.CASCADE,
        related_name="program_partner_through",
    )
    partner = models.ForeignKey(
        "account.Partner",
        on_delete=models.CASCADE,
        related_name="program_partner_through",
    )
    areas = models.ManyToManyField("geo.Area", related_name="program_partner_through", blank=True)
    full_area_access = models.BooleanField(default=False)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["program", "partner"],
                name="unique_program_partner",
            )
        ]


class BeneficiaryGroup(TimeStampedUUIDModel):
    name = models.CharField(max_length=255, unique=True)
    group_label = models.CharField(max_length=255)
    group_label_plural = models.CharField(max_length=255)
    member_label = models.CharField(max_length=255)
    member_label_plural = models.CharField(max_length=255)
    master_detail = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Beneficiary Group"
        verbose_name_plural = "Beneficiary Groups"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Program(SoftDeletableModel, TimeStampedUUIDModel, AbstractSyncable, ConcurrencyModel, AdminUrlMixin):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "name",
            "status",
            "start_date",
            "end_date",
            "description",
            "business_area",
            "budget",
            "frequency_of_payments",
            "sector",
            "scope",
            "cash_plus",
            "population_goal",
            "administrative_areas_of_implementation",
            "partner_access",
        ],
        {"admin_areas_log": "admin_areas"},
    )
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"
    STATUS_CHOICE = (
        (ACTIVE, _("Active")),
        (DRAFT, _("Draft")),
        (FINISHED, _("Finished")),
    )

    REGULAR = "REGULAR"
    ONE_OFF = "ONE_OFF"

    FREQUENCY_OF_PAYMENTS_CHOICE = (
        (ONE_OFF, _("One-off")),
        (REGULAR, _("Regular")),
    )

    CHILD_PROTECTION = "CHILD_PROTECTION"
    EDUCATION = "EDUCATION"
    HEALTH = "HEALTH"
    MULTI_PURPOSE = "MULTI_PURPOSE"
    NUTRITION = "NUTRITION"
    SOCIAL_POLICY = "SOCIAL_POLICY"
    WASH = "WASH"

    SECTOR_CHOICE = (
        (CHILD_PROTECTION, _("Child Protection")),
        (EDUCATION, _("Education")),
        (HEALTH, _("Health")),
        (MULTI_PURPOSE, _("Multi Purpose")),
        (NUTRITION, _("Nutrition")),
        (SOCIAL_POLICY, _("Social Policy")),
        (WASH, _("WASH")),
    )

    SCOPE_FOR_PARTNERS = "FOR_PARTNERS"
    SCOPE_UNICEF = "UNICEF"

    SCOPE_CHOICE = (
        (SCOPE_FOR_PARTNERS, _("For partners")),
        (SCOPE_UNICEF, _("Unicef")),
    )

    ALL_PARTNERS_ACCESS = "ALL_PARTNERS_ACCESS"
    NONE_PARTNERS_ACCESS = "NONE_PARTNERS_ACCESS"
    SELECTED_PARTNERS_ACCESS = "SELECTED_PARTNERS_ACCESS"

    PARTNER_ACCESS_CHOICE = (
        (ALL_PARTNERS_ACCESS, _("All partners access")),
        (NONE_PARTNERS_ACCESS, _("None partners access")),
        (SELECTED_PARTNERS_ACCESS, _("Selected partners access")),
    )

    name = CICharField(
        max_length=255,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(255),
            DoubleSpaceValidator,
            StartEndSpaceValidator,
            ProhibitNullCharactersValidator(),
        ],
        db_index=True,
    )
    programme_code = models.CharField(max_length=4, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, db_index=True)
    description = models.CharField(
        blank=True,
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(null=True, blank=True, db_index=True)
    data_collecting_type = models.ForeignKey(
        "core.DataCollectingType", related_name="programs", on_delete=models.PROTECT
    )
    beneficiary_group = models.ForeignKey(
        BeneficiaryGroup,
        on_delete=models.PROTECT,
        related_name="programs",
    )
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    admin_areas = models.ManyToManyField("geo.Area", related_name="programs", blank=True)
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICE, db_index=True)
    budget = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        validators=[MinValueValidator(Decimal("0.00"))],
        db_index=True,
    )
    frequency_of_payments = models.CharField(
        max_length=50,
        choices=FREQUENCY_OF_PAYMENTS_CHOICE,
    )
    scope = models.CharField(
        blank=True,
        null=True,
        max_length=50,
        choices=SCOPE_CHOICE,
    )
    partners = models.ManyToManyField(to="account.Partner", through=ProgramPartnerThrough, related_name="programs")
    partner_access = models.CharField(
        max_length=50,
        choices=PARTNER_ACCESS_CHOICE,
        default=SELECTED_PARTNERS_ACCESS,
    )
    cash_plus = models.BooleanField()
    population_goal = models.PositiveIntegerField()
    administrative_areas_of_implementation = models.CharField(
        max_length=255,
        blank=True,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    is_visible = models.BooleanField(default=True)
    household_count = models.PositiveIntegerField(default=0)
    individual_count = models.PositiveIntegerField(default=0)

    deduplication_set_id = models.UUIDField(blank=True, null=True)
    biometric_deduplication_enabled = models.BooleanField(
        default=False, help_text="Enable Deduplication of Face Images"
    )
    collision_detection_enabled = models.BooleanField(default=False, help_text="don't create duplicated")
    collision_detector = StrategyField(
        registry=collision_detectors_registry, null=True, blank=True, help_text="Object which detects collisions"
    )

    objects = SoftDeletableIsVisibleManager()

    def clean(self) -> None:
        super().clean()
        if self.data_collecting_type and self.beneficiary_group:
            if (
                self.data_collecting_type.type == DataCollectingType.Type.SOCIAL
                and self.beneficiary_group.master_detail
            ) or (
                self.data_collecting_type.type == DataCollectingType.Type.STANDARD
                and not self.beneficiary_group.master_detail
            ):
                raise ValidationError("Selected combination of data collecting type and beneficiary group is invalid.")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        if not self.programme_code:
            self.programme_code = self._generate_programme_code()
        if self.data_collecting_type_id is None and self.data_collecting_type:
            # save the related object before saving Program
            self.data_collecting_type.save()
        super().save(*args, **kwargs)

    def _generate_programme_code(self) -> str:
        programme_code = "".join(random.choice(string.ascii_uppercase + string.digits + "-/.") for _ in range(4))
        if Program.objects.filter(business_area_id=self.business_area_id, programme_code=programme_code).exists():
            return self._generate_programme_code()
        return programme_code

    @staticmethod
    def get_total_number_of_households_from_payments(qs: models.QuerySet[PaymentPlan]) -> int:
        return (
            qs.filter(**{"payment_items__delivered_quantity__gt": 0})
            .distinct("payment_items__household__unicef_id")
            .values_list("payment_items__household__unicef_id", flat=True)
            .order_by("payment_items__household__unicef_id")
            .count()
        )

    def adjust_program_size(self) -> None:
        self.household_count = self.household_set.count()
        self.individual_count = self.individuals.count()

    @property
    def households_with_payments_in_program(self) -> QuerySet:
        # for now all Payments or maybe can filter just status__in=Payment.DELIVERED_STATUSES
        household_ids = (
            Payment.objects.filter(program=self)
            .exclude(conflicted=True, excluded=True)
            .values_list("household_id", flat=True)
            .distinct()
        )

        return Household.objects.filter(id__in=household_ids, program=self)

    @property
    def admin_areas_log(self) -> str:
        return ", ".join(self.admin_areas.all())

    @property
    def is_social_worker_program(self) -> bool:
        return self.data_collecting_type.type == DataCollectingType.Type.SOCIAL

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["name", "business_area", "is_removed"],
                condition=Q(is_removed=False),
                name="unique_for_program_if_not_removed",
            ),
            UniqueConstraint(
                fields=["business_area", "programme_code"],
                condition=Q(is_removed=False),
                name="unique_for_business_area_and_programme_code_if_not_removed",
            ),
        ]
        permissions = [("enroll_beneficiaries", "Can enroll beneficiaries")]
        verbose_name = "Programme"

    def __str__(self) -> str:
        return self.name

    def validate_unique(self, exclude: Optional[Collection[str]] = ...) -> None:  # type: ignore
        query = Program.objects.filter(name=self.name, business_area=self.business_area, is_removed=False)
        if query.exists() and query.first() != self:
            raise ValidationError(
                f"Program for name: {self.name} and business_area: {self.business_area.slug} already exists."
            )
        super(Program, self).validate_unique()

    def is_active(self) -> bool:
        return self.status == self.ACTIVE

    @property
    def can_finish(self) -> bool:
        return not self.cycles.filter(status=ProgramCycle.ACTIVE).exists()


class ProgramCycle(AdminUrlMixin, TimeStampedUUIDModel, UnicefIdentifiedModel, ConcurrencyModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "title",
            "status",
            "start_date",
            "end_date",
            "created_by",
        ],
    )
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"
    STATUS_CHOICE = (
        (DRAFT, _("Draft")),
        (ACTIVE, _("Active")),
        (FINISHED, _("Finished")),
    )
    title = models.CharField(_("Title"), max_length=255, null=True, blank=True, default="Default Programme Cycle")
    program = models.ForeignKey("Program", on_delete=models.CASCADE, related_name="cycles")
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, db_index=True, default=DRAFT)
    start_date = models.DateField()  # first from program
    end_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Created by"),
        related_name="+",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["title", "program"],
                name="program_cycle_title_unique_per_program",
            ),
        ]
        ordering = ["start_date"]
        verbose_name = "Programme Cycle"

    def clean(self) -> None:
        start_date = parse_date(self.start_date) if isinstance(self.start_date, str) else self.start_date
        end_date = parse_date(self.end_date) if isinstance(self.end_date, str) else self.end_date

        if end_date and end_date < start_date:
            raise ValidationError("End date cannot be before start date.")

        if self._state.adding and self.program.cycles.exclude(pk=self.pk).filter(end_date__gte=start_date).exists():
            raise ValidationError("Start date must be after the latest cycle.")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} ({self.status})"

    @property
    def can_remove_cycle(self) -> bool:
        return not self.payment_plans.exists() and self.program.cycles.count() > 1 and self.status == ProgramCycle.DRAFT

    @property
    def total_entitled_quantity_usd(self) -> Decimal:
        total_entitled_usd = self.payment_plans.aggregate(total_entitled_usd=Sum("total_entitled_quantity_usd"))[
            "total_entitled_usd"
        ]
        return total_entitled_usd or Decimal(0.0)

    @property
    def total_undelivered_quantity_usd(self) -> Decimal:
        total_undelivered_usd = self.payment_plans.aggregate(
            total_undelivered_usd=Sum("total_undelivered_quantity_usd")
        )["total_undelivered_usd"]
        return total_undelivered_usd or Decimal(0.0)

    @property
    def total_delivered_quantity_usd(self) -> Decimal:
        total_delivered_usd = self.payment_plans.aggregate(total_delivered_usd=Sum("total_delivered_quantity_usd"))[
            "total_delivered_usd"
        ]
        return total_delivered_usd or Decimal(0.0)

    @property
    def program_start_date(self) -> date:
        return self.program.start_date

    @property
    def program_end_date(self) -> date:
        return self.program.end_date

    @property
    def frequency_of_payments(self) -> str:
        return self.program.get_frequency_of_payments_display()

    def validate_program_active_status(self) -> None:
        # all changes with Program Cycle are possible within Active Program
        if self.program.status != Program.ACTIVE:
            raise DRFValidationError("Program should be within Active status.")

    def validate_payment_plan_status(self) -> None:
        from hct_mis_api.apps.payment.models import PaymentPlan

        if (
            PaymentPlan.objects.filter(program_cycle=self)
            .exclude(
                status__in=[PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED],
            )
            .exists()
        ):
            raise DRFValidationError("All Payment Plans and Follow-Up Payment Plans have to be Reconciled.")

    def set_active(self) -> None:
        self.validate_program_active_status()
        if self.status in (ProgramCycle.DRAFT, ProgramCycle.FINISHED):
            self.status = ProgramCycle.ACTIVE
            self.save()

    def set_draft(self) -> None:
        self.validate_program_active_status()
        if self.status == ProgramCycle.ACTIVE:
            self.status = ProgramCycle.DRAFT
            self.save()

    def set_finish(self) -> None:
        self.validate_program_active_status()
        self.validate_payment_plan_status()
        if self.status == ProgramCycle.ACTIVE:
            self.status = ProgramCycle.FINISHED
            self.save()
