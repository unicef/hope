# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestActionMessageMutation::test_get_communication_message_sample_size_for_households_0_with_permission_and_full_list_households 1'] = {
    'data': {
        'accountabilityCommunicationMessageSampleSize': {
            'numberOfRecipients': 4,
            'sampleSize': 4
        }
    }
}

snapshots['TestActionMessageMutation::test_get_communication_message_sample_size_for_households_1_with_permission_and_random_households 1'] = {
    'data': {
        'accountabilityCommunicationMessageSampleSize': {
            'numberOfRecipients': 4,
            'sampleSize': 1
        }
    }
}

snapshots['TestActionMessageMutation::test_get_communication_message_sample_size_for_rdi_0_with_permission_and_full_list_rdi 1'] = {
    'data': {
        'accountabilityCommunicationMessageSampleSize': {
            'numberOfRecipients': 0,
            'sampleSize': 0
        }
    }
}

snapshots['TestActionMessageMutation::test_get_communication_message_sample_size_for_rdi_1_with_permission_and_random_rdi 1'] = {
    'data': {
        'accountabilityCommunicationMessageSampleSize': {
            'numberOfRecipients': 0,
            'sampleSize': 0
        }
    }
}

snapshots['TestActionMessageMutation::test_get_communication_message_sample_size_for_target_population_0_with_permission_and_full_list_tp 1'] = {
    'data': {
        'accountabilityCommunicationMessageSampleSize': {
            'numberOfRecipients': 4,
            'sampleSize': 4
        }
    }
}

snapshots['TestActionMessageMutation::test_get_communication_message_sample_size_for_target_population_1_with_permission_and_random_tp 1'] = {
    'data': {
        'accountabilityCommunicationMessageSampleSize': {
            'numberOfRecipients': 4,
            'sampleSize': 1
        }
    }
}

snapshots['TestActionMessageMutation::test_get_communication_message_sample_size_for_target_population_2_without_permission_full_list_tp 1'] = {
    'data': {
        'accountabilityCommunicationMessageSampleSize': {
            'numberOfRecipients': 4,
            'sampleSize': 4
        }
    }
}

snapshots['TestActionMessageMutation::test_get_communication_message_sample_size_for_target_population_3_without_permission_random_tp 1'] = {
    'data': {
        'accountabilityCommunicationMessageSampleSize': {
            'numberOfRecipients': 4,
            'sampleSize': 1
        }
    }
}
