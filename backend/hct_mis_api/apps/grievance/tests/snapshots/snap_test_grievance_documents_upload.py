# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGrievanceDocumentsUpload::test_mutation_creates_and_deletes_documents_for_existing_grievance_ticket_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'admin': 'City Test',
                'category': 6,
                'consent': True,
                'documentation': [
                    {
                        'contentType': 'image/jpeg',
                        'fileSize': 2048,
                        'name': 'created_scanned_document1'
                    }
                ]
            }
        }
    }
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_creates_and_deletes_documents_for_existing_grievance_ticket_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_creates_and_updates_documents_for_existing_grievance_ticket_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'admin': 'City Test',
                'category': 6,
                'consent': True,
                'documentation': [
                    {
                        'contentType': 'image/jpeg',
                        'fileSize': 666,
                        'name': 'created_scanned_document1'
                    },
                    {
                        'contentType': 'image/jpeg',
                        'fileSize': 1048576,
                        'name': 'updated_document.jpg'
                    }
                ]
            }
        }
    }
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_creates_and_updates_documents_for_existing_grievance_ticket_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_creates_documents_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Feedback tickets are not allowed to be created through this mutation.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_creates_documents_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_creates_file_for_allowed_types_0_some_document_jpg 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Feedback tickets are not allowed to be created through this mutation.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_creates_file_for_allowed_types_1_some_document_png 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Feedback tickets are not allowed to be created through this mutation.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_creates_file_for_allowed_types_2_some_document_tiff 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Feedback tickets are not allowed to be created through this mutation.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_creates_file_for_allowed_types_3_some_document_pdf 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Feedback tickets are not allowed to be created through this mutation.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_creates_single_document_for_existing_grievance_ticket_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'admin': 'City Test',
                'category': 6,
                'consent': True,
                'documentation': [
                    {
                        'contentType': 'image/jpeg',
                        'fileSize': 2048,
                        'name': 'scanned_document1'
                    }
                ]
            }
        }
    }
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_creates_single_document_for_existing_grievance_ticket_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_creates_updates_deletes_documents_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'admin': 'City Test',
                'category': 6,
                'consent': True,
                'documentation': [
                    {
                        'contentType': 'image/jpeg',
                        'fileSize': 666,
                        'name': 'created_scanned_document1'
                    },
                    {
                        'contentType': 'image/jpeg',
                        'fileSize': 1048576,
                        'name': 'updated_document.jpg'
                    }
                ]
            }
        }
    }
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_creates_updates_deletes_documents_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_deletes_non_existing_document_for_existing_grievance_ticket_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'admin': 'City Test',
                'category': 6,
                'consent': True,
                'documentation': [
                ]
            }
        }
    }
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_deletes_non_existing_document_for_existing_grievance_ticket_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_deletes_single_document_for_existing_grievance_ticket_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'admin': 'City Test',
                'category': 6,
                'consent': True,
                'documentation': [
                ]
            }
        }
    }
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_deletes_single_document_for_existing_grievance_ticket_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_raises_error_when_not_allowed_type_file_is_uploaded_0_some_document_css 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Feedback tickets are not allowed to be created through this mutation.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_raises_error_when_not_allowed_type_file_is_uploaded_1_some_document_html 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Feedback tickets are not allowed to be created through this mutation.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_raises_error_when_total_size_of_uploaded_files_is_bigger_than_25mb_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Feedback tickets are not allowed to be created through this mutation.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_raises_error_when_total_size_of_uploaded_files_is_bigger_than_25mb_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_raises_error_when_uploaded_file_is_bigger_than_3mb_0_with_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Feedback tickets are not allowed to be created through this mutation.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_raises_error_when_uploaded_file_is_bigger_than_3mb_1_without_permission 1'] = {
    'data': {
        'createGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 3
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'createGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_updates_non_existing_documents_for_existing_grievance_ticket_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'admin': 'City Test',
                'category': 6,
                'consent': True,
                'documentation': [
                ]
            }
        }
    }
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_updates_non_existing_documents_for_existing_grievance_ticket_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_updates_single_document_for_existing_grievance_ticket_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': {
            'grievanceTicket': {
                'admin': 'City Test',
                'category': 6,
                'consent': True,
                'documentation': [
                    {
                        'contentType': 'image/jpeg',
                        'fileSize': 1048576,
                        'name': 'updated_document.jpg'
                    }
                ]
            }
        }
    }
}

snapshots['TestGrievanceDocumentsUpload::test_mutation_updates_single_document_for_existing_grievance_ticket_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_raises_error_when_mutation_updates_document_with_size_5mb_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'File scanned_document_update.jpg of size 5242880 is above max size limit',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_raises_error_when_mutation_updates_document_with_size_5mb_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_raises_error_when_mutation_updates_documents_above_25mb_limit_0_with_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Adding/Updating of new files exceed 25mb maximum size of files',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}

snapshots['TestGrievanceDocumentsUpload::test_raises_error_when_mutation_updates_documents_above_25mb_limit_1_without_permission 1'] = {
    'data': {
        'updateGrievanceTicket': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 11,
                    'line': 5
                }
            ],
            'message': 'Permission Denied: User does not have correct permission.',
            'path': [
                'updateGrievanceTicket'
            ]
        }
    ]
}
