from typing import Any, List

import factory
from factory.django import DjangoModelFactory
from faker import Faker

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.core.models import BusinessArea
from hope.apps.periodic_data_update.models import (
    PDUOnlineEdit,
    PDUOnlineEditSentBackComment,
    PDUXlsxTemplate,
    PDUXlsxUpload,
)

fake = Faker()


class PDUXlsxTemplateFactory(DjangoModelFactory):
    class Meta:
        model = PDUXlsxTemplate

    name = factory.Faker("word")
    created_by = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice([choice[0] for choice in PDUXlsxTemplate.Status.choices])
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    program = factory.SubFactory(ProgramFactory)
    number_of_records = fake.random_int(min=1, max=100)
    rounds_data = factory.LazyAttribute(
        lambda _: [
            {
                "field": fake.sentence(nb_words=3),
                "round": fake.random_int(min=1, max=10),
                "round_name": fake.sentence(nb_words=3),
                "number_of_records": fake.random_int(min=1, max=100),
            }
            for _ in range(2)
        ]
    )
    filters = {}


class PDUXlsxUploadFactory(DjangoModelFactory):
    class Meta:
        model = PDUXlsxUpload

    created_by = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice([choice[0] for choice in PDUXlsxUpload.Status.choices])
    template = factory.SubFactory(PDUXlsxTemplateFactory)


class PDUOnlineEditFactory(DjangoModelFactory):
    class Meta:
        model = PDUOnlineEdit

    name = factory.Faker("word")
    created_by = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice([choice[0] for choice in PDUOnlineEdit.Status.choices])
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    program = factory.SubFactory(ProgramFactory)
    number_of_records = fake.random_int(min=1, max=100)
    edit_data = {}

    @factory.post_generation
    def authorized_users(self, create: bool, extracted: List[Any], **kwargs: Any):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.authorized_users.add(user)


class PDUOnlineEditSentBackCommentFactory(DjangoModelFactory):
    class Meta:
        model = PDUOnlineEditSentBackComment

    comment = factory.Faker("sentence")
    created_by = factory.SubFactory(UserFactory)
    pdu_online_edit = factory.SubFactory(PDUOnlineEditFactory)
