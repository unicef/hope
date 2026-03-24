"""Periodic data update factories."""

from typing import Any, List

import factory
from factory.django import DjangoModelFactory

from hope.models import PDUOnlineEdit, PDUOnlineEditSentBackComment, PDUXlsxTemplate, PDUXlsxUpload

from .account import UserFactory
from .core import BusinessAreaFactory
from .program import ProgramFactory


class PDUXlsxTemplateFactory(DjangoModelFactory):
    class Meta:
        model = PDUXlsxTemplate

    name = factory.Sequence(lambda n: f"Template {n}")
    created_by = factory.SubFactory(UserFactory)
    status = PDUXlsxTemplate.Status.TO_EXPORT
    business_area = factory.SubFactory(BusinessAreaFactory)
    program = factory.SubFactory(ProgramFactory)
    number_of_records = 10
    rounds_data = factory.LazyAttribute(
        lambda _: [
            {
                "field": "field_1",
                "round": 1,
                "round_name": "Round 1",
                "number_of_records": 10,
            }
        ]
    )
    filters = {}


class PDUXlsxUploadFactory(DjangoModelFactory):
    class Meta:
        model = PDUXlsxUpload

    created_by = factory.SubFactory(UserFactory)
    status = PDUXlsxUpload.Status.SUCCESSFUL
    template = factory.SubFactory(PDUXlsxTemplateFactory)
    file = factory.django.FileField(filename="test.xlsx")


class PDUOnlineEditFactory(DjangoModelFactory):
    class Meta:
        model = PDUOnlineEdit

    name = factory.Sequence(lambda n: f"Online Edit {n}")
    created_by = factory.SubFactory(UserFactory)
    status = PDUOnlineEdit.Status.NEW
    business_area = factory.SubFactory(BusinessAreaFactory)
    program = factory.SubFactory(ProgramFactory)
    number_of_records = 10
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

    comment = factory.Sequence(lambda n: f"Sent Back Comment {n}")
    created_by = factory.SubFactory(UserFactory)
    pdu_online_edit = factory.SubFactory(PDUOnlineEditFactory)
