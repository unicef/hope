from django.dispatch import Signal

grievance_assignment_changed = Signal()
grievance_deduplication_created = Signal()
grievance_notes_added = Signal()
grievance_overdue = Signal()
grievance_payment_verification_created = Signal()
grievance_sent_back_to_in_progress = Signal()
grievance_sent_to_approval = Signal()
grievance_sensitive_created = Signal()
grievance_sensitive_overdue = Signal()
grievance_system_flagging_created = Signal()
