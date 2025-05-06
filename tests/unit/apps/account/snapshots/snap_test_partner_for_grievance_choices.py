# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["PartnerForGrievanceTest::test_partner_choices_with_program 1"] = {
    "data": {"partnerForGrievanceChoices": [{"name": "Partner with access to Test Program"}, {"name": "UNICEF"}]}
}

snapshots["PartnerForGrievanceTest::test_partner_choices_without_program_and_without_household_and_individual 1"] = {
    "data": {
        "partnerForGrievanceChoices": [
            {"name": "Partner with access to Test Program"},
            {"name": "Partner with access to Test Program for Household"},
            {"name": "Partner with with access to Test Program Any"},
            {"name": "UNICEF"},
        ]
    }
}

snapshots["PartnerForGrievanceTest::test_partner_choices_without_program_but_with_household 1"] = {
    "data": {
        "partnerForGrievanceChoices": [
            {"name": "Partner with access to Test Program for Household"},
            {"name": "UNICEF"},
        ]
    }
}

snapshots["PartnerForGrievanceTest::test_partner_choices_without_program_but_with_individual 1"] = {
    "data": {
        "partnerForGrievanceChoices": [
            {"name": "Partner with access to Test Program for Household"},
            {"name": "UNICEF"},
        ]
    }
}
