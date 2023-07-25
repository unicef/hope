# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestFSPRelatedSchema::test_query_all_financial_service_provider_xlsx_reports 1'] = {
    'data': {
        'allFinancialServiceProviderXlsxReports': {
            'edges': [
                {
                    'node': {
                        'financialServiceProvider': {
                            'name': 'FSP_1'
                        },
                        'status': 2
                    }
                },
                {
                    'node': {
                        'financialServiceProvider': {
                            'name': 'FSP_2'
                        },
                        'status': 1
                    }
                }
            ]
        }
    }
}

snapshots['TestFSPRelatedSchema::test_query_all_financial_service_provider_xlsx_templates 1'] = {
    'data': {
        'allFinancialServiceProviderXlsxTemplates': {
            'edges': [
                {
                    'node': {
                        'columns': [
                            'column_1',
                            'column_2'
                        ],
                        'name': 'FSP_template_1'
                    }
                },
                {
                    'node': {
                        'columns': [
                            'column_3',
                            'column_4'
                        ],
                        'name': 'FSP_template_2'
                    }
                }
            ]
        }
    }
}

snapshots['TestFSPRelatedSchema::test_query_all_financial_service_providers 1'] = {
    'data': {
        'allFinancialServiceProviders': {
            'edges': [
                {
                    'node': {
                        'communicationChannel': 'XLSX',
                        'deliveryMechanisms': [
                            'Cash'
                        ],
                        'name': 'FSP_1',
                        'visionVendorNumber': '149-69-3686'
                    }
                },
                {
                    'node': {
                        'communicationChannel': 'API',
                        'deliveryMechanisms': [
                            'Voucher'
                        ],
                        'name': 'FSP_2',
                        'visionVendorNumber': '666-69-3686'
                    }
                }
            ]
        }
    }
}

snapshots['TestFSPRelatedSchema::test_query_single_financial_service_provider 1'] = {
    'data': {
        'financialServiceProvider': {
            'distributionLimit': 10000.0,
            'name': 'FSP_1',
            'visionVendorNumber': '149-69-3686'
        }
    }
}

snapshots['TestFSPRelatedSchema::test_query_single_financial_service_provider_xlsx_report 1'] = {
    'data': {
        'financialServiceProviderXlsxReport': {
            'financialServiceProvider': {
                'name': 'FSP_1'
            },
            'status': 2
        }
    }
}

snapshots['TestFSPRelatedSchema::test_query_single_financial_service_provider_xlsx_template 1'] = {
    'data': {
        'financialServiceProviderXlsxTemplate': {
            'columns': [
                'column_1',
                'column_2'
            ],
            'name': 'FSP_template_1'
        }
    }
}
