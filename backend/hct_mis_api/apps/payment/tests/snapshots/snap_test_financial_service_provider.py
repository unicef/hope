# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestAllFinancialServiceProviders::test_create_financial_service_provider 1'] = {
    'data': {
        'createFinancialServiceProvider': {
            'financialServiceProvider': {
                'communicationChannel': 'XLSX',
                'deliveryMechanisms': 'email',
                'distributionLimit': 123456789.0,
                'fspXlsxTemplate': {
                    'createdAt': '2022-07-14T12:52:22.700351',
                    'createdBy': None,
                    'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTpjNjhmMzlhNy02NjdjLTQzNGYtOTc0Mi1mNmRkZjAzNDZhNDY=',
                    'name': ''
                },
                'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTo4ZmM2ZTNjNi1hOTkwLTRkMjAtOTAwNy02NzAzMWU0ZWUwMWQ=',
                'name': 'Web3 Bank',
                'visionVendorNumber': 'XYZB-123456789'
            }
        }
    }
}

snapshots['TestAllFinancialServiceProviders::test_fetch_all_financial_service_providers 1'] = {
    'data': {
        'allFinancialServiceProviders': {
            'edges': [
                {
                    'node': {
                        'createdAt': '2022-07-14T12:52:22.232183',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTowZDRlNmQ5ZC0wNjZjLTQzNzItOGVkOC1mZWRjMDU0ZTRkMjk=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTpjNTBmMjBjMy0yYTExLTQ5MzUtYThhNC04OTNkYzcyMTNmOWQ='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-14T12:52:22.238725',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTozOTlkNmIzOS1mZTU2LTQwNmMtOWQ0OS1lNzU4M2Q1MDMzMmM=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZToyMjE5NjRmZC1lNjRmLTQ2MmMtOWNhNC04MTA0MjYxOGM2YzY='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-14T12:52:22.246360',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZToxYThiYWFjYy03MWJkLTQ0NGItYTU1ZC0wOGZjZDVkZTYyYWM=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTphMmE4MDZkZC03MWM1LTQ2NmYtYTQxNC1jYjRlNTNjYTFiNjY='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-14T12:52:22.253487',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTo2MmZmZTg3NS00YzM5LTQyODEtYmRkOS1kMzljMTRhZTQ0YjE=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZToyMDlhNGFkNS04NDE3LTQ0ZGEtYTY4NC1hOWZhMGZhNmZmNmU='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-14T12:52:22.260403',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTowODEwZDA2MC0wNzQ4LTRhZGYtYjg0My0zMDBhYWRlNjFhYjg=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTo5OTBmODgxMC0xNzU2LTQ2NjYtOTI1NS0yNDU0OTE2MjAyYTI='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-14T12:52:22.267463',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTo1OTY4MWI3MS00ZDMwLTQ5YWItODMyMy0zYjA1NDc0MDc3Y2Q=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTo1Y2M1MTkxMy00NjQ5LTQ0ZDgtYjdmNC1jMWUzYjEyZjA5NGY='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-14T12:52:22.273856',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTpmYmM4MTRlMS02NGYxLTQxOGQtYTg4ZC02ZDUwZDkzMmVmMDk=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTpmMmM4OGY3ZS03YTQ1LTQ4MGItODUwOS01MGQzM2IwYWRhZjY='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-14T12:52:22.280732',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZToxYzFlN2ZmNS0yYjcwLTQ1ZDYtOTkzZi1iOTc2NDYxNjJlMDA=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTo0Nzc3ZWJiOC1iMDIyLTRhMTktODA4OS01ZTAzMDY4ZjdjMTQ='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-14T12:52:22.286979',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTplZTk3ZWQ2NC02Mjc3LTRjYzctOTM5OS01NTczZDQ5YmQ3N2E=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTo1MGYxYmIyMC1jOGQwLTQ4ZWMtYjNjMi1mMTZiOWMzYmEzNTc='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-14T12:52:22.293329',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTo5NDVhNDUxMi1hZDdiLTQ3MTUtODEwNC01MTZiNDJlMGY3MzA=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTphOGEyMzg4Yy1kMTU4LTQ1Y2EtOGI3OS0zMDNkNzljN2Y2M2M='
                    }
                }
            ]
        }
    }
}

snapshots['TestAllFinancialServiceProviders::test_fetch_count_financial_service_providers 1'] = {
    'data': {
        'allFinancialServiceProviders': {
            'edgeCount': 10,
            'totalCount': 10
        }
    }
}

snapshots['TestAllFinancialServiceProviders::test_update_financial_service_provider 1'] = {
    'data': {
        'editFinancialServiceProvider': {
            'financialServiceProvider': {
                'communicationChannel': 'XLSX',
                'deliveryMechanisms': 'email',
                'distributionLimit': 123456789.0,
                'fspXlsxTemplate': {
                    'createdAt': '2022-07-14T12:52:22.849785',
                    'createdBy': None,
                    'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTpkMGNhMTg2My1hODMzLTRjMGQtOGQ5Yi1mYTcxMjM5MmEwNWQ=',
                    'name': ''
                },
                'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTo0Yzg3NTI2Yi1mZTZiLTRmOTctYjRjYy0wZGFlNmM1Zjc4Mzk=',
                'name': 'New Gen Bank',
                'visionVendorNumber': 'XYZB-123456789'
            }
        }
    }
}
