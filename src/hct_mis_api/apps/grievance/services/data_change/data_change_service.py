import abc
from typing import Dict, List

from django.contrib.auth.models import AbstractUser

from hct_mis_api.apps.grievance.models import GrievanceTicket


class DataChangeService(abc.ABC):
    def __init__(self, grievance_ticket: GrievanceTicket, extras: Dict) -> None:
        self.grievance_ticket = grievance_ticket
        self.extras = extras

    @abc.abstractmethod
    def save(self) -> List[GrievanceTicket]:
        pass

    @abc.abstractmethod
    def update(self) -> GrievanceTicket:
        pass

    @abc.abstractmethod
    def close(self, user: AbstractUser) -> None:
        pass
