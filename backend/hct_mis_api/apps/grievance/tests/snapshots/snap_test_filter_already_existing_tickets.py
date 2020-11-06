# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestAlreadyExistingFilterTickets::test_filter_existing_tickets_by_payment_record 1'] = {
    'data': {
        'existingGrievanceTickets': {
            'edges': [
                {
                    'node': {
                        'area': 'Body win lead investment out they beyond imagine.',
                        'category': 3,
                        'sensitiveTicketDetails': {
                            'household': {
                                'size': 1
                            },
                            'individual': {
                                'fullName': 'John Doe'
                            },
                            'paymentRecord': {
                                'fullName': 'John Doe'
                            }
                        },
                        'status': 1
                    }
                }
            ]
        }
    }
}

snapshots['TestAlreadyExistingFilterTickets::test_filter_existing_tickets_by_household 1'] = {
    'data': {
        'existingGrievanceTickets': {
            'edges': [
                {
                    'node': {
                        'area': 'Economy recently often them writer trip.',
                        'category': 3,
                        'sensitiveTicketDetails': {
                            'household': {
                                'size': 1
                            },
                            'individual': {
                                'fullName': 'John Doe'
                            },
                            'paymentRecord': {
                                'fullName': 'John Doe'
                            }
                        },
                        'status': 4
                    }
                },
                {
                    'node': {
                        'area': 'Land trial reflect answer old which company.',
                        'category': 3,
                        'sensitiveTicketDetails': {
                            'household': {
                                'size': 1
                            },
                            'individual': {
                                'fullName': 'John Doe'
                            },
                            'paymentRecord': {
                                'fullName': 'John Doe'
                            }
                        },
                        'status': 4
                    }
                },
                {
                    'node': {
                        'area': 'People act step store.',
                        'category': 3,
                        'sensitiveTicketDetails': {
                            'household': {
                                'size': 1
                            },
                            'individual': {
                                'fullName': 'John Doe'
                            },
                            'paymentRecord': None
                        },
                        'status': 5
                    }
                }
            ]
        }
    }
}

snapshots['TestAlreadyExistingFilterTickets::test_filter_existing_tickets_by_individual 1'] = {
    'data': {
        'existingGrievanceTickets': {
            'edges': [
                {
                    'node': {
                        'area': 'Unit other prepare mention word institution.',
                        'category': 3,
                        'sensitiveTicketDetails': {
                            'household': {
                                'size': 1
                            },
                            'individual': {
                                'fullName': 'John Doe'
                            },
                            'paymentRecord': None
                        },
                        'status': 1
                    }
                },
                {
                    'node': {
                        'area': 'During improve choose draw peace against course.',
                        'category': 3,
                        'sensitiveTicketDetails': {
                            'household': {
                                'size': 1
                            },
                            'individual': {
                                'fullName': 'John Doe'
                            },
                            'paymentRecord': {
                                'fullName': 'John Doe'
                            }
                        },
                        'status': 2
                    }
                },
                {
                    'node': {
                        'area': 'Piece while name including color.',
                        'category': 3,
                        'sensitiveTicketDetails': {
                            'household': {
                                'size': 1
                            },
                            'individual': {
                                'fullName': 'John Doe'
                            },
                            'paymentRecord': {
                                'fullName': 'John Doe'
                            }
                        },
                        'status': 3
                    }
                }
            ]
        }
    }
}

snapshots['TestAlreadyExistingFilterTickets::test_filter_existing_tickets_by_two_payment_records 1'] = {
    'data': {
        'existingGrievanceTickets': {
            'edges': [
                {
                    'node': {
                        'area': 'Attorney language member instead.',
                        'category': 3,
                        'sensitiveTicketDetails': {
                            'household': {
                                'size': 1
                            },
                            'individual': {
                                'fullName': 'John Doe'
                            },
                            'paymentRecord': {
                                'fullName': 'John Doe'
                            }
                        },
                        'status': 5
                    }
                },
                {
                    'node': {
                        'area': 'Of sport full plan customer throw.',
                        'category': 3,
                        'sensitiveTicketDetails': {
                            'household': {
                                'size': 1
                            },
                            'individual': {
                                'fullName': 'John Doe'
                            },
                            'paymentRecord': {
                                'fullName': 'John Doe'
                            }
                        },
                        'status': 5
                    }
                }
            ]
        }
    }
}
