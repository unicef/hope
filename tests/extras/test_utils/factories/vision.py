"""Vision-related factories."""

import factory
from factory.django import DjangoModelFactory

from hope.contrib.vision.models import FundsCommitmentGroup, FundsCommitmentItem


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
