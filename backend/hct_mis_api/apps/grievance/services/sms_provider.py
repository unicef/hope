import abc
from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    number: str
    message: str


class SmsProvider(abc.ABC):
    @abc.abstractmethod
    def send(self, phone_number: str, message: str):
        pass

    @abc.abstractmethod
    def receive_messages(self) -> list[Message]:
        pass


class TwilioSmsProvider(SmsProvider):
    def send(self, phone_number: str, message: str):
        # TODO implement twilio
        pass

    def receive_messages(self) -> list[Message]:
        # TODO implement twilio
        pass


def get_sms_provider() -> SmsProvider:
    return TwilioSmsProvider()
