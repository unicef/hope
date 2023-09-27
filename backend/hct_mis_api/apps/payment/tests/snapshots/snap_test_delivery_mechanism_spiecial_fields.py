# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestDeliveryMechanismSpecialFields::test_delivery_mechanism_contain_bank_data 1'] = {
    'data': {
        'payment': {
            'deliveryMechanism': {
                'bankAccountNumber': '12345678900987654',
                'bankName': 'ing',
                'cardNumber': None,
                'phoneNo': None
            },
            'documents': [
                {
                    'documentNumber': '777888999',
                    'type': {
                        'key': 'tax_id'
                    }
                }
            ]
        }
    }
}

snapshots['TestDeliveryMechanismSpecialFields::test_delivery_mechanism_contain_card_number 1'] = {
    'data': {
        'payment': {
            'deliveryMechanism': {
                'bankAccountNumber': None,
                'bankName': None,
                'cardNumber': '1234567890',
                'phoneNo': None
            },
            'documents': [
                {
                    'documentNumber': '111222333',
                    'type': {
                        'key': 'national_id'
                    }
                }
            ]
        }
    }
}

snapshots['TestDeliveryMechanismSpecialFields::test_delivery_mechanism_contain_mobile_phone_number 1'] = {
    'data': {
        'payment': {
            'deliveryMechanism': {
                'bankAccountNumber': None,
                'bankName': None,
                'cardNumber': None,
                'phoneNo': '+48654789123'
            },
            'documents': [
                {
                    'documentNumber': '444555666',
                    'type': {
                        'key': 'national_passport'
                    }
                }
            ]
        }
    }
}
