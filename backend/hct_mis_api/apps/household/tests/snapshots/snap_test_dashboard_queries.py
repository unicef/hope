# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDashboardQueries::test_charts_0_chartIndividualsReachedByAgeAndGender 1'] = {
    'data': {
        'chartIndividualsReachedByAgeAndGender': {
            'datasets': [
                {
                    'data': [
                        8.0,
                        4.0,
                        4.0,
                        4.0,
                        4.0,
                        0.0,
                        4.0,
                        0.0,
                        4.0,
                        6.0
                    ]
                }
            ],
            'labels': [
                'Females 0-5',
                'Females 6-11',
                'Females 12-17',
                'Females 18-59',
                'Females 60+',
                'Males 0-5',
                'Males 6-11',
                'Males 12-17',
                'Males 18-59',
                'Males 60+'
            ]
        }
    }
}

snapshots['TestDashboardQueries::test_charts_1_chartIndividualsWithDisabilityReachedByAge 1'] = {
    'data': {
        'chartIndividualsWithDisabilityReachedByAge': {
            'datasets': [
                {
                    'data': [
                        4.0,
                        0.0,
                        0.0,
                        2.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        4.0
                    ],
                    'label': 'with disability'
                },
                {
                    'data': [
                        4.0,
                        4.0,
                        4.0,
                        2.0,
                        4.0,
                        0.0,
                        4.0,
                        0.0,
                        4.0,
                        2.0
                    ],
                    'label': 'without disability'
                },
                {
                    'data': [
                        8.0,
                        4.0,
                        4.0,
                        4.0,
                        4.0,
                        0.0,
                        4.0,
                        0.0,
                        4.0,
                        6.0
                    ],
                    'label': 'total'
                }
            ],
            'labels': [
                'Females 0-5',
                'Females 6-11',
                'Females 12-17',
                'Females 18-59',
                'Females 60+',
                'Males 0-5',
                'Males 6-11',
                'Males 12-17',
                'Males 18-59',
                'Males 60+'
            ]
        }
    }
}

snapshots['TestDashboardQueries::test_sections_0_sectionHouseholdsReached 1'] = {
    'data': {
        'sectionHouseholdsReached': {
            'total': 4.0
        }
    }
}

snapshots['TestDashboardQueries::test_sections_1_sectionIndividualsReached 1'] = {
    'data': {
        'sectionIndividualsReached': {
            'total': 38.0
        }
    }
}

snapshots['TestDashboardQueries::test_sections_2_sectionChildReached 1'] = {
    'data': {
        'sectionChildReached': {
            'total': 20.0
        }
    }
}
