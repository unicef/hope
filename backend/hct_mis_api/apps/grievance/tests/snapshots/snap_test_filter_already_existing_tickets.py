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
                        }
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
                        }
                    }
                },
                {
                    'node': {
                        'category': 3,
                        'sensitiveTicketDetails': {
                            'household': {
                                'size': 1
                            },
                            'individual': {
                                'fullName': 'John Doe'
                            },
                            'paymentRecord': None
                        }
                    }
                },
                {
                    'node': {
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
                        }
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
                        }
                    }
                },
                {
                    'node': {
                        'category': 3,
                        'sensitiveTicketDetails': {
                            'household': {
                                'size': 1
                            },
                            'individual': {
                                'fullName': 'John Doe'
                            },
                            'paymentRecord': None
                        }
                    }
                },
                {
                    'node': {
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
                        }
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
                        }
                    }
                },
                {
                    'node': {
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
                        }
                    }
                }
            ]
        }
    }
}
