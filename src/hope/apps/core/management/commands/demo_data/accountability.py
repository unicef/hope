from extras.test_utils.factories import CommunicationMessageFactory, FeedbackFactory
from hope.models import BusinessArea, Household, Program, User


def generate_messages() -> None:
    ba = BusinessArea.objects.get(slug="afghanistan")
    user_root = User.objects.get(username="root")
    program = Program.objects.get(name="Test Program")
    households = Household.objects.filter(program=program)
    hh_1 = households.first()
    hh_2 = households.last()

    msg_data = [
        {
            "unicef_id": "MSG-22-0001",
            "title": "Hello World!",
            "body": "World is beautiful, don't mess with it!",
            "created_by": user_root,
            "program": program,
            "number_of_recipients": 2,
            "business_area": ba,
            "registration_data_import": None,
            "sampling_type": "RANDOM",
            "full_list_arguments": None,
            "random_sampling_arguments": {
                "age": {"max": 2, "min": 1},
                "sex": "any",
                "margin_of_error": 20.0,
                "confidence_interval": 0.9,
                "excluded_admin_areas": [],
            },
            "sample_size": 0,
        },
        {
            "unicef_id": "MSG-22-0004",
            "title": "You got credit of USD 200",
            "body": "Greetings {recipient_full_name}, we have sent you USD 200 in your registered account on "
            "{rp_timestamp}",
            "created_by": user_root,
            "program": program,
            "number_of_recipients": 2,
            "business_area": ba,
            "registration_data_import": None,
            "sampling_type": "RANDOM",
            "full_list_arguments": None,
            "random_sampling_arguments": {
                "age": {"max": 2, "min": 1},
                "sex": "any",
                "margin_of_error": 80.0,
                "confidence_interval": 0.8,
                "excluded_admin_areas": [],
            },
            "sample_size": 0,
        },
        {
            "unicef_id": "MSG-22-0002",
            "title": "Hello There!",
            "body": "Hey, there. Welcome to the party!",
            "created_by": user_root,
            "program": program,
            "number_of_recipients": 2,
            "business_area": ba,
            "registration_data_import": None,
            "sampling_type": "RANDOM",
            "full_list_arguments": None,
            "random_sampling_arguments": {
                "age": {"max": 2, "min": 1},
                "sex": "any",
                "margin_of_error": 20.0,
                "confidence_interval": 0.9,
                "excluded_admin_areas": [],
            },
            "sample_size": 0,
        },
        {
            "unicef_id": "MSG-22-0003",
            "title": "We hold your back!",
            "body": "Hey XYZ, don't be worry. We UNICEF are here to help to grow!",
            "created_by": user_root,
            "program": program,
            "number_of_recipients": 2,
            "business_area": ba,
            "registration_data_import": None,
            "sampling_type": "FULL_LIST",
            "full_list_arguments": {"excluded_admin_areas": []},
            "random_sampling_arguments": None,
            "sample_size": 2,
        },
    ]
    for msg in msg_data:
        msg_obj = CommunicationMessageFactory(**msg)
        msg_obj.households.set([hh_1, hh_2])


def generate_feedback() -> None:
    ba = BusinessArea.objects.get(slug="afghanistan")
    feedback_data = [
        {
            "business_area": ba,
            "issue_type": "POSITIVE_FEEDBACK",
            "description": "Positive Feedback",
        },
        {
            "business_area": ba,
            "issue_type": "NEGATIVE_FEEDBACK",
            "description": "Negative Feedback",
        },
    ]
    feedback_positive = FeedbackFactory(**feedback_data[0])
    feedback_positive.unicef_id = "FED-23-0001"
    feedback_positive.save()
    feedback_negative = FeedbackFactory(**feedback_data[1])
    feedback_negative.unicef_id = "FED-23-0002"
    feedback_negative.save()
