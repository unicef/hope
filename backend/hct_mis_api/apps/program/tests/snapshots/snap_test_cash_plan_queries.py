# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestCashPlanQueries::test_get_single_cash_plan 1'] = {
    'data': {
        'cashPlan': {
            'assistanceThrough': 'Cairo Amman Bank',
            'cashAssistId': '7ff3542c-8c48-4ed4-8283-41966093995b',
            'coverageDuration': 21,
            'coverageUnits': 'Day(s)',
            'currency': 'Syrian pound',
            'deliveryType': 'Deposit to Card',
            'disbursementDate': '2064-03-09T22:52:54',
            'dispersionDate': '2020-04-25',
            'distributionModality': '994-94',
            'dpId': '951-84-9815',
            'endDate': '2064-03-14T22:52:54',
            'fcId': '965-79-7961',
            'fsp': 'Sullivan Group',
            'name': 'Far yet reveal area bar almost dinner.',
            'numberOfHouseholds': 540,
            'startDate': '2051-11-30T00:02:09',
            'status': 'NOT_STARTED',
            'totalDeliveredQuantity': 53477453.27,
            'totalEntitledQuantity': 56657648.82,
            'totalUndeliveredQuantity': 55497021.04
        }
    }
}

snapshots['TestCashPlanQueries::test_get_all_cash_plans 1'] = {
    'data': {
        'allCashPlans': {
            'edges': [
                {
                    'node': {
                        'assistanceThrough': 'Cairo Amman Bank',
                        'cashAssistId': '7ff3542c-8c48-4ed4-8283-41966093995b',
                        'coverageDuration': 21,
                        'coverageUnits': 'Day(s)',
                        'currency': 'Syrian pound',
                        'deliveryType': 'Deposit to Card',
                        'disbursementDate': '2064-03-09T22:52:54',
                        'dispersionDate': '2020-04-25',
                        'distributionModality': '994-94',
                        'dpId': '951-84-9815',
                        'endDate': '2064-03-14T22:52:54',
                        'fcId': '965-79-7961',
                        'fsp': 'Sullivan Group',
                        'name': 'Far yet reveal area bar almost dinner.',
                        'numberOfHouseholds': 540,
                        'startDate': '2051-11-30T00:02:09',
                        'status': 'NOT_STARTED',
                        'totalDeliveredQuantity': 53477453.27,
                        'totalEntitledQuantity': 56657648.82,
                        'totalUndeliveredQuantity': 55497021.04
                    }
                },
                {
                    'node': {
                        'assistanceThrough': 'Cairo Amman Bank',
                        'cashAssistId': '04b9d44b-67fe-425c-9095-509e31ba7494',
                        'coverageDuration': 19,
                        'coverageUnits': 'Week(s)',
                        'currency': 'Cuban peso',
                        'deliveryType': 'Deposit to Card',
                        'disbursementDate': '2028-03-26T18:44:15',
                        'dispersionDate': '2020-02-22',
                        'distributionModality': '513-17',
                        'dpId': '966-76-0951',
                        'endDate': '2028-03-31T18:44:15',
                        'fcId': '913-72-9949',
                        'fsp': 'Fox-Moody',
                        'name': 'Despite action TV after.',
                        'numberOfHouseholds': 100,
                        'startDate': '2041-06-14T10:15:44',
                        'status': 'COMPLETE',
                        'totalDeliveredQuantity': 41935107.03,
                        'totalEntitledQuantity': 38204833.92,
                        'totalUndeliveredQuantity': 63098825.46
                    }
                },
                {
                    'node': {
                        'assistanceThrough': 'Cairo Amman Bank',
                        'cashAssistId': 'e02e9e29-a9bc-4d72-9c95-23fe123662c4',
                        'coverageDuration': 29,
                        'coverageUnits': 'Day(s)',
                        'currency': 'Swazi lilangeni',
                        'deliveryType': 'Deposit to Card',
                        'disbursementDate': '2077-02-25T19:04:32',
                        'dispersionDate': '2020-08-13',
                        'distributionModality': '126-33',
                        'dpId': '901-88-1631',
                        'endDate': '2077-03-02T19:04:32',
                        'fcId': '964-90-7586',
                        'fsp': 'Allen-Vargas',
                        'name': 'Tonight lay range sometimes serious program.',
                        'numberOfHouseholds': 198,
                        'startDate': '2075-03-04T08:54:21',
                        'status': 'COMPLETE',
                        'totalDeliveredQuantity': 67021407.24,
                        'totalEntitledQuantity': 71574231.27,
                        'totalUndeliveredQuantity': 68666170.96
                    }
                },
                {
                    'node': {
                        'assistanceThrough': 'Cairo Amman Bank',
                        'cashAssistId': '0772b884-0ae1-4d4b-823d-80037eef00af',
                        'coverageDuration': 24,
                        'coverageUnits': 'Week(s)',
                        'currency': 'Peruvian sol',
                        'deliveryType': 'Deposit to Card',
                        'disbursementDate': '2024-04-17T10:59:34',
                        'dispersionDate': '2021-01-04',
                        'distributionModality': '581-10',
                        'dpId': '920-92-3896',
                        'endDate': '2024-04-22T10:59:34',
                        'fcId': '908-94-6201',
                        'fsp': 'Walsh-Johnson',
                        'name': 'Worry degree current.',
                        'numberOfHouseholds': 454,
                        'startDate': '2065-01-02T00:00:10',
                        'status': 'STARTED',
                        'totalDeliveredQuantity': 77590217.09,
                        'totalEntitledQuantity': 45129411.47,
                        'totalUndeliveredQuantity': 31657176.41
                    }
                },
                {
                    'node': {
                        'assistanceThrough': 'Cairo Amman Bank',
                        'cashAssistId': '357eeb74-f76d-4f12-a02b-8e67f0f90813',
                        'coverageDuration': 17,
                        'coverageUnits': 'Day(s)',
                        'currency': 'Philippine peso',
                        'deliveryType': 'Deposit to Card',
                        'disbursementDate': '2032-08-04T19:20:26',
                        'dispersionDate': '2020-07-03',
                        'distributionModality': '388-88',
                        'dpId': '910-84-7232',
                        'endDate': '2032-08-09T19:20:26',
                        'fcId': '936-79-6145',
                        'fsp': 'Strickland, Flores and Robertson',
                        'name': 'Wide our office trip.',
                        'numberOfHouseholds': 227,
                        'startDate': '2092-04-11T02:06:37',
                        'status': 'STARTED',
                        'totalDeliveredQuantity': 41956165.06,
                        'totalEntitledQuantity': 23032305.51,
                        'totalUndeliveredQuantity': 71567447.8
                    }
                },
                {
                    'node': {
                        'assistanceThrough': 'Cairo Amman Bank',
                        'cashAssistId': 'be4fcbf6-40ba-405d-86be-0010c19a91c4',
                        'coverageDuration': 26,
                        'coverageUnits': 'Week(s)',
                        'currency': 'Serbian dinar',
                        'deliveryType': 'Deposit to Card',
                        'disbursementDate': '2020-04-15T17:51:54',
                        'dispersionDate': '2020-05-13',
                        'distributionModality': '857-37',
                        'dpId': '940-88-0908',
                        'endDate': '2020-04-20T17:51:54',
                        'fcId': '907-71-7905',
                        'fsp': 'Stone, Carpenter and Jones',
                        'name': 'Just study road leg little.',
                        'numberOfHouseholds': 140,
                        'startDate': '2045-04-01T18:24:31',
                        'status': 'COMPLETE',
                        'totalDeliveredQuantity': 75231429.04,
                        'totalEntitledQuantity': 6478697.79,
                        'totalUndeliveredQuantity': 19931436.71
                    }
                },
                {
                    'node': {
                        'assistanceThrough': 'Cairo Amman Bank',
                        'cashAssistId': '17502569-0613-44f2-94d0-916ad6a7b860',
                        'coverageDuration': 14,
                        'coverageUnits': 'Month(s)',
                        'currency': 'Albanian lek',
                        'deliveryType': 'Deposit to Card',
                        'disbursementDate': '2036-06-24T11:08:43',
                        'dispersionDate': '2020-07-25',
                        'distributionModality': '386-44',
                        'dpId': '925-82-8201',
                        'endDate': '2036-06-29T11:08:43',
                        'fcId': '996-79-0175',
                        'fsp': 'Mcknight-Stewart',
                        'name': 'Six quickly level want left response become.',
                        'numberOfHouseholds': 261,
                        'startDate': '2067-07-03T01:23:31',
                        'status': 'STARTED',
                        'totalDeliveredQuantity': 58925502.75,
                        'totalEntitledQuantity': 71489015.63,
                        'totalUndeliveredQuantity': 58316677.75
                    }
                },
                {
                    'node': {
                        'assistanceThrough': 'Cairo Amman Bank',
                        'cashAssistId': 'ccd0b2b1-85dc-44c2-82f3-906b33a16645',
                        'coverageDuration': 12,
                        'coverageUnits': 'Week(s)',
                        'currency': 'Falkland Islands pound',
                        'deliveryType': 'Deposit to Card',
                        'disbursementDate': '2093-10-02T09:41:06',
                        'dispersionDate': '2020-03-27',
                        'distributionModality': '053-54',
                        'dpId': '901-83-9734',
                        'endDate': '2093-10-07T09:41:06',
                        'fcId': '975-71-8876',
                        'fsp': 'Fitzpatrick-Garcia',
                        'name': 'Our everybody anyone which whom western cultural.',
                        'numberOfHouseholds': 366,
                        'startDate': '2091-09-04T16:58:02',
                        'status': 'COMPLETE',
                        'totalDeliveredQuantity': 47098878.58,
                        'totalEntitledQuantity': 24371399.57,
                        'totalUndeliveredQuantity': 31178307.82
                    }
                },
                {
                    'node': {
                        'assistanceThrough': 'Cairo Amman Bank',
                        'cashAssistId': '0d4f1c5e-7f83-4f8a-9a9c-82a2af883a83',
                        'coverageDuration': 18,
                        'coverageUnits': 'Year(s)',
                        'currency': 'Hong Kong dollar',
                        'deliveryType': 'Deposit to Card',
                        'disbursementDate': '2045-12-16T00:24:00',
                        'dispersionDate': '2020-03-25',
                        'distributionModality': '361-32',
                        'dpId': '994-79-6154',
                        'endDate': '2045-12-21T00:24:00',
                        'fcId': '987-92-6540',
                        'fsp': 'Mueller Group',
                        'name': 'Maybe resource eight remember.',
                        'numberOfHouseholds': 175,
                        'startDate': '2087-01-16T01:15:41',
                        'status': 'COMPLETE',
                        'totalDeliveredQuantity': 63827276.43,
                        'totalEntitledQuantity': 41776487.16,
                        'totalUndeliveredQuantity': 76468590.87
                    }
                },
                {
                    'node': {
                        'assistanceThrough': 'Cairo Amman Bank',
                        'cashAssistId': '056d6d6e-2562-4f1e-a37d-00017020a869',
                        'coverageDuration': 27,
                        'coverageUnits': 'Month(s)',
                        'currency': 'Seborga luigino',
                        'deliveryType': 'Deposit to Card',
                        'disbursementDate': '2034-06-28T03:05:26',
                        'dispersionDate': '2020-03-19',
                        'distributionModality': '949-96',
                        'dpId': '915-92-3393',
                        'endDate': '2034-07-03T03:05:26',
                        'fcId': '921-81-6446',
                        'fsp': 'Harris-Lin',
                        'name': 'Suggest call civil natural single side if cut.',
                        'numberOfHouseholds': 403,
                        'startDate': '2086-04-18T10:59:10',
                        'status': 'COMPLETE',
                        'totalDeliveredQuantity': 21181440.08,
                        'totalEntitledQuantity': 73287521.63,
                        'totalUndeliveredQuantity': 29600156.58
                    }
                }
            ]
        }
    }
}
