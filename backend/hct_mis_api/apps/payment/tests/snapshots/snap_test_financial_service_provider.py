# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestAllFinancialServiceProviders::test_create_financial_service_provider 1'] = {
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 4
                }
            ],
            'message': '''Variable "$input" got invalid value {"communicationChannel": "email", "dataTransferConfiguration": {"dataTransferType": "ftp", "ftpConfiguration": {"directory": "/", "host": "ftp.example.com", "password": "password", "port": 21, "username": "username"}}, "distributionLimit": "123456789", "name": "FSP Name", "visionVendorNumber": "123456789"}.
In field "dataTransferConfiguration": Unknown field.
In field "distributionLimit": Unknown field.
In field "deliveryMechanisms": Expected "String!", found null.
In field "fspXlsxTemplateId": Expected "ID!", found null.'''
        }
    ]
}

snapshots['TestAllFinancialServiceProviders::test_fetch_all_financial_service_providers 1'] = {
    'data': {
        'allFinancialServiceProviders': {
            'edges': [
                {
                    'node': {
                        'createdAt': '2022-07-13T11:56:02.683042',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTozMzkxNGEzNi03YmQyLTQ0ZjQtYTNlYi1jMWJmMjFjZGY2ODc=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTo3NjdmNjcxMi0wMTA3LTRjNmMtOTkxYS0yZDI2MmIyZDNmOTE='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-13T11:56:02.691608',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTplYWM0MDlkMS0zNzMwLTQ2OTctOTEwMy1lYzhjNGRhMmFmZDE=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZToyZjFhZThkNC1mODFlLTRlZWYtODg2OC0wMzY2NWI1MmE1Yzk='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-13T11:56:02.699293',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTpjMzMyN2Q2MC1iMDZlLTQ4NDktOTFhYy0wYjQ5ZDQ2ZmI3NzM=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTozYWY1NTFmNC04NDEwLTQzNzEtYWJlMy02ZWE1N2M2ZWFhMWU='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-13T11:56:02.706574',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTo5OGI3OTg3NS0xZWViLTQyODYtYmI5ZS1hYWEyZTQ3YzdhMDY=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTplODE2ZDU2Ni1mZjk5LTRiYTYtYWE1Yy1lYjQxNmU4MzJkYTA='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-13T11:56:02.713535',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTpjZGE5YmI3ZS01ZTE2LTQ5ODMtYWFmNi0xYzVmZTRlNjUzNDQ=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTozMDY5MjI5Zi05YjNhLTQ3NDAtYmFkYS05YzRjYWMyNTYzNGE='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-13T11:56:02.720326',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTpjYzMyODEyZC1jZGExLTRhZmEtYWJmYi0wNDhkZWVjYWQyYTI=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTowM2UwZGRkNC04YWY3LTQxMDctYWZmMS1kN2Y1MWM2YmU0OTY='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-13T11:56:02.727257',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTo1ZTc4NTdmYy03ZWI4LTQ1MDMtOTgyZC01MWIzNzk0ZDIwYjM=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTo3NTAxMWFjYy03MzdkLTQ4YzAtOTg1Zi05ZDcxNzY0MTY5M2Q='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-13T11:56:02.734767',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTplMDc1ZWUzZC00MjdiLTQzOWItYWNiNy1jYTc3NGRmM2U1OTM=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTpkMzNhZGJlMy1iYTZiLTQ3MzktOTY2Ny0xZjYyMzY4ZDBkODQ='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-13T11:56:02.741716',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTozZGY3OTViYy1mNDRkLTRjODItYmY0OC1jZDNkZTQ3ODM2MTY=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTo2YWYzYTA0Yi1kMGMzLTRkZGMtYmEyNy1hMjNjZDg5MzAzMzk='
                    }
                },
                {
                    'node': {
                        'createdAt': '2022-07-13T11:56:02.748059',
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        },
                        'fspXlsxTemplate': {
                            'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyWGxzeFRlbXBsYXRlTm9kZTpjZWE3OTQxYS0zOGFhLTQ0OTAtYTVjMC01MWM3YzU4NzI4MDU=',
                            'name': ''
                        },
                        'id': 'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTo0YTc1ZGUxNy00Yjk5LTRlOTMtODI3OC1lNTc2ZGVjOTM5NTE='
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
