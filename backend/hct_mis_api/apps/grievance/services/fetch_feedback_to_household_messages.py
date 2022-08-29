from hct_mis_api.apps.grievance.services.rapid_pro import RapidPro


def fetch_feedback_to_household_messages():
    rapid_pro_service = RapidPro()
    messages = rapid_pro_service.fetch_feedback_to_household_messages()
