# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestHouseholdRegistrationId::test_household_program_detail_id_0_ABCD_123123 1'] = {
    'data': {
        'household': {
            'programRegistrationId': 'ABCD-123123'
        }
    }
}

snapshots['TestHouseholdRegistrationId::test_household_program_detail_id_1 1'] = {
    'data': {
        'household': {
            'programRegistrationId': None
        }
    }
}

snapshots['TestHouseholdRegistrationId::test_household_program_detail_id_2_ 1'] = {
    'data': {
        'household': {
            'programRegistrationId': None
        }
    }
}

snapshots['TestHouseholdRegistrationId::test_household_program_registration_id_0_ABCD_123123 1'] = {
    'data': {
        'household': {
            'programRegistrationId': 'ABCD-123123'
        }
    }
}

snapshots['TestHouseholdRegistrationId::test_household_program_registration_id_1 1'] = {
    'data': {
        'household': {
            'programRegistrationId': None
        }
    }
}

snapshots['TestHouseholdRegistrationId::test_household_program_registration_id_2_ 1'] = {
    'data': {
        'household': {
            'programRegistrationId': None
        }
    }
}
