# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestHouseholdPermissionsQuery::test_not_unicef_partner_with_program_and_with_correct_admin_area_has_access_for_program 1'] = {
    'data': {
        'household': {
            'admin2': {
                'pCode': 'TEST0101'
            },
            'size': 2
        }
    }
}

snapshots['TestHouseholdPermissionsQuery::test_not_unicef_partner_with_program_and_with_correct_admin_area_has_access_query_all_programs 1'] = {
    'data': {
        'household': {
            'admin2': {
                'pCode': 'TEST0101'
            },
            'size': 2
        }
    }
}

snapshots['TestHouseholdPermissionsQuery::test_not_unicef_partner_with_program_and_with_full_admin_area_has_access_for_program 1'] = {
    'data': {
        'household': {
            'admin2': {
                'pCode': 'TEST0101'
            },
            'size': 2
        }
    }
}

snapshots['TestHouseholdPermissionsQuery::test_not_unicef_partner_with_program_and_with_full_admin_area_has_access_query_all_programs 1'] = {
    'data': {
        'household': {
            'admin2': {
                'pCode': 'TEST0101'
            },
            'size': 2
        }
    }
}

snapshots['TestHouseholdPermissionsQuery::test_not_unicef_partner_with_program_and_with_wrong_admin_area_doesnt_have_access_for_program 1'] = {
    'data': {
        'household': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'household'
            ]
        }
    ]
}

snapshots['TestHouseholdPermissionsQuery::test_not_unicef_partner_with_program_and_with_wrong_admin_area_doesnt_have_access_query_all_programs 1'] = {
    'data': {
        'household': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'household'
            ]
        }
    ]
}

snapshots['TestHouseholdPermissionsQuery::test_not_unicef_partner_without_program_doesnt_have_access_for_program 1'] = {
    'data': {
        'household': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'household'
            ]
        }
    ]
}

snapshots['TestHouseholdPermissionsQuery::test_not_unicef_partner_without_program_doesnt_have_access_query_all_programs 1'] = {
    'data': {
        'household': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 7,
                    'line': 3
                }
            ],
            'message': 'Permission Denied',
            'path': [
                'household'
            ]
        }
    ]
}

snapshots['TestHouseholdPermissionsQuery::test_unicef_partner_has_access_for_program 1'] = {
    'data': {
        'household': {
            'admin2': {
                'pCode': 'TEST0101'
            },
            'size': 2
        }
    }
}

snapshots['TestHouseholdPermissionsQuery::test_unicef_partner_has_access_query_all_programs 1'] = {
    'data': {
        'household': {
            'admin2': {
                'pCode': 'TEST0101'
            },
            'size': 2
        }
    }
}
