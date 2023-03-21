# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestAllFinancialServiceProviders::test_create_financial_service_provider 1'] = {
    'errors': [
        {
            'message': 'Object of type set is not JSON serializable'
        }
    ]
}

snapshots['TestAllFinancialServiceProviders::test_fetch_all_financial_service_providers 1'] = {
    'data': {
        'allFinancialServiceProviders': {
            'edges': [
                {
                    'node': {
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        }
                    }
                },
                {
                    'node': {
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        }
                    }
                },
                {
                    'node': {
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        }
                    }
                },
                {
                    'node': {
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        }
                    }
                },
                {
                    'node': {
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        }
                    }
                },
                {
                    'node': {
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        }
                    }
                },
                {
                    'node': {
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        }
                    }
                },
                {
                    'node': {
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        }
                    }
                },
                {
                    'node': {
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        }
                    }
                },
                {
                    'node': {
                        'financialserviceproviderxlsxreportSet': {
                            'edges': [
                            ]
                        }
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
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 5
                }
            ],
            'message': '''Variable "$inputs" got invalid value {"communicationChannel": "XLSX", "deliveryMechanisms": ["Transfer", "Cash"], "distributionLimit": "100999", "name": "New Gen Bank", "visionVendorNumber": "XYZB-123456799"}.
In field "fspXlsxTemplateId": Expected "ID!", found null.'''
        }
    ]
}
