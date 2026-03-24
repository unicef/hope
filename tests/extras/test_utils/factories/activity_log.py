"""Activity log factories."""

import factory
from factory.django import DjangoModelFactory

from hope.models import LogEntry

from .account import UserFactory
from .core import BusinessAreaFactory


class LogEntryFactory(DjangoModelFactory):
    class Meta:
        model = LogEntry

    action = LogEntry.CREATE
    object_repr = factory.Sequence(lambda n: f"Object {n}")
    business_area = factory.SubFactory(BusinessAreaFactory)
    user = factory.SubFactory(UserFactory)

    @factory.post_generation
    def programs(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for program in extracted:
                self.programs.add(program)
