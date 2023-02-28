# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDashboardQueries::test_chart_total_transferred_by_country 1'] = {
    'data': {
        'chartTotalTransferredCashByCountry': {
            'datasets': [
                {
                    'data': [
                        80.0,
                        88.0,
                        84.0
                    ],
                    'label': 'Actual cash transferred'
                },
                {
                    'data': [
                        40.0,
                        44.0,
                        42.0
                    ],
                    'label': 'Actual voucher transferred'
                },
                {
                    'data': [
                        120.0,
                        132.0,
                        126.0
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

snapshots['TestDashboardQueries::test_charts_0_chartVolumeByDeliveryMechanism 1'] = {
    'data': {
        'chartVolumeByDeliveryMechanism': {
            'datasets': [
                {
                    'data': [
                        80.0,
                        40.0
                    ]
                }
            ],
            'labels': [
                'Cash',
                'Voucher'
            ]
        }
    }
}

snapshots['TestDashboardQueries::test_charts_1_chartPayment 1'] = {
    'data': {
        'chartPayment': {
            'datasets': [
                {
                    'data': [
                        4.0,
                        2.0
                    ]
                }
            ],
            'labels': [
                'Successful Payments',
                'Unsuccessful Payments'
            ]
        }
    }
}

snapshots['TestDashboardQueries::test_sections_0_sectionTotalTransferred 1'] = {
    'data': {
        'sectionTotalTransferred': {
            'total': 120.0
        }
    }
}

snapshots['TestDashboardQueries::test_table_total_cash_transferred_by_administrative_area 1'] = {
    'data': {
        'tableTotalCashTransferredByAdministrativeArea': {
            'data': [
                {
                    'admin2': 'afghanistan city 1',
                    'totalCashTransferred': 20.0,
                    'totalHouseholds': 2
                },
                {
                    'admin2': 'afghanistan city 2',
                    'totalCashTransferred': 40.0,
                    'totalHouseholds': 2
                },
                {
                    'admin2': 'afghanistan city 3',
                    'totalCashTransferred': 60.0,
                    'totalHouseholds': 2
                }
            ]
        }
    }
}
