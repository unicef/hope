# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDashboardQueries::test_chart_programmes_by_sector 1'] = {
    'data': {
        'chartProgrammesBySector': {
            'datasets': [
                {
                    'data': [
                        0.0,
                        1.0,
                        1.0,
                        0.0
                    ],
                    'label': 'Programmes'
                },
                {
                    'data': [
                        1.0,
                        0.0,
                        0.0,
                        1.0
                    ],
                    'label': 'Programmes with Cash+'
                },
                {
                    'data': [
                        1.0,
                        1.0,
                        1.0,
                        1.0
                    ],
                    'label': 'Total Programmes'
                }
            ],
            'labels': [
                'Education',
                'Health',
                'Nutrition',
                'WASH'
            ]
        }
    }
}

snapshots['TestDashboardQueries::test_chart_total_transferred_by_month 1'] = {
    'data': {
        'chartTotalTransferredByMonth': {
            'datasets': [
                {
                    'data': [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        316.0,
                        632.0
                    ],
                    'label': 'Previous Transfers'
                },
                {
                    'data': [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        50.0,
                        50.0,
                        0.0
                    ],
                    'label': 'Voucher Transferred'
                },
                {
                    'data': [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        266.0,
                        266.0,
                        0.0
                    ],
                    'label': 'Cash Transferred'
                }
            ],
            'labels': [
                'Jan',
                'Feb',
                'Mar',
                'Apr',
                'May',
                'Jun',
                'Jul',
                'Aug',
                'Sep',
                'Oct',
                'Nov',
                'Dec'
            ]
        }
    }
}
