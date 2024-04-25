# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestHouseholdRegistrationId::test_household_registration_id_0_ABCD_123123_0 1'] = {
    'data': {
        'household': {
            'registrationId': 'ABCD-123123'
        }
    }
}

snapshots['TestHouseholdRegistrationId::test_household_registration_id_1_ABCD_123123_1 1'] = {
    'data': {
        'household': {
            'registrationId': 'ABCD-123123'
        }
    }
}

snapshots['TestHouseholdRegistrationId::test_household_registration_id_2 1'] = {
    'data': {
        'household': {
            'registrationId': None
        }
    }
}

snapshots['TestHouseholdRegistrationId::test_household_registration_id_3_ 1'] = {
    'data': {
        'household': {
            'registrationId': None
        }
    }
}
