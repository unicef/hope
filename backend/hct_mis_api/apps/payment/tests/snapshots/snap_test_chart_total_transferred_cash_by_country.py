# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['TestChartTotalTransferredCashByCountry::test_resolving_chart_0_with_permission 1'] = {
    'data': {
        'chartTotalTransferredCashByCountry': {
            'datasets': [
                {
                    'data': [
                        600.6,
                        600.6,
                        600.6
                    ],
                    'label': 'Actual cash transferred'
                },
                {
                    'data': [
                        300.0,
                        300.0,
                        300.0
                    ],
                    'label': 'Actual voucher transferred'
                },
                {
                    'data': [
                        900.6,
                        900.6,
                        900.6
                    ],
                    'label': 'Total transferred'
                }
            ],
            'labels': [
                'Afghanistan',
                'Angola',
                'Botswana'
            ]
        }
    }
}

snapshots['TestChartTotalTransferredCashByCountry::test_resolving_chart_1_without_permission 1'] = {
    'data': {
        'chartTotalTransferredCashByCountry': None
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
                'chartTotalTransferredCashByCountry'
            ]
        }
    ]
}
