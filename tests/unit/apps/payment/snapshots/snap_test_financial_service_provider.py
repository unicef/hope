# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestAllFinancialServiceProviders::test_fetch_all_financial_service_providers 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Cannot query field "allFinancialServiceProviders" on type "Query".'
        }
    ]
}

snapshots['TestAllFinancialServiceProviders::test_fetch_count_financial_service_providers 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 3
                }
            ],
            'message': 'Cannot query field "allFinancialServiceProviders" on type "Query".'
        }
    ]
}
