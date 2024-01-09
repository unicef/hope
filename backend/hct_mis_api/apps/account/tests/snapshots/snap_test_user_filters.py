# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestUserFilter::test_users_by_business_area 1'] = {
    'data': {
        'allUsers': {
            'edges': [
                {
                    'node': {
                        'partner': {
                            'name': 'UNICEF'
                        },
                        'username': 'unicef_user'
                    }
                },
                {
                    'node': {
                        'partner': {
                            'name': 'Default Empty Partner'
                        },
                        'username': 'user_in_ba'
                    }
                },
                {
                    'node': {
                        'partner': {
                            'name': 'Test Partner'
                        },
                        'username': 'user_with_partner_in_ba'
                    }
                }
            ]
        }
    }
}
