from constance import config


def get_grievance_notification_hour() -> int:
    return int(config.GRIEVANCE_NOTIFICATION_HOUR)
