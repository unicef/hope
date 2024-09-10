from django.dispatch import Signal

individual_withdrawn = Signal()
household_withdrawn = Signal()
household_deleted = Signal()
individual_deleted = Signal()
