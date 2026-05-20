"""Vision-related factories."""

import factory
from factory.django import DjangoModelFactory

from hope.contrib.vision.models import DownPayment, FundsCommitment, FundsCommitmentGroup, FundsCommitmentItem


class FundsCommitmentGroupFactory(DjangoModelFactory):
    class Meta:
        model = FundsCommitmentGroup

    funds_commitment_number = factory.Sequence(lambda n: f"FC{n:06d}")


class FundsCommitmentItemFactory(DjangoModelFactory):
    class Meta:
        model = FundsCommitmentItem

    funds_commitment_group = factory.SubFactory(FundsCommitmentGroupFactory)
    funds_commitment_item = factory.Sequence(lambda n: f"{n % 1000:03d}")
    rec_serial_number = factory.Sequence(lambda n: n + 1)
    office = None


class FundsCommitmentFactory(DjangoModelFactory):
    class Meta:
        model = FundsCommitment

    rec_serial_number = factory.Sequence(lambda n: n + 1)
    funds_commitment_number = factory.Sequence(lambda n: f"FC{n:06d}")


class DownPaymentFactory(DjangoModelFactory):
    class Meta:
        model = DownPayment

    rec_serial_number = factory.Sequence(lambda n: n + 1)
    business_area = factory.Sequence(lambda n: f"{n:04d}")
    down_payment_reference = factory.Sequence(lambda n: f"DPR{n:010d}")
    document_type = factory.Sequence(lambda n: f"T{n % 10}")
    consumed_fc_number = factory.Sequence(lambda n: f"FC{n:06d}")
    total_down_payment_amount_local = 0
