from enum import StrEnum


class VisionLogEntryType(StrEnum):
    API_CALL = "api-call"
    PUSH_NOTIFICATION = "push-notification"


class VisionStatus(StrEnum):
    NOT_SENT = "NOT_SENT"
    SEND_FAILED = "SEND_FAILED"
    WAITING_FOR_CALLBACK = "WAITING_FOR_CALLBACK"
    CALLBACK_FAILED = "CALLBACK_FAILED"
    FC_MISSING = "FC_MISSING"
    FC_NOT_FOUND = "FC_NOT_FOUND"
    FC_ASSOCIATED = "FC_ASSOCIATED"
    RELEASED = "RELEASED"


VISION_SEND_MUTABLE_STATUSES = frozenset(
    {
        VisionStatus.NOT_SENT.value,
        VisionStatus.SEND_FAILED.value,
        VisionStatus.WAITING_FOR_CALLBACK.value,
    }
)


class VisionErrorCode(StrEnum):
    FC_AMBIGUOUS = "FC_AMBIGUOUS"
    FC_CONFLICT = "FC_CONFLICT"
    VISION_STATUS_FAILED = "VISION_STATUS_FAILED"
