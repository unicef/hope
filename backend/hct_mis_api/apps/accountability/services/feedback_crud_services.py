from django.contrib.auth import get_user_model
from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.core.models import BusinessArea

User = get_user_model()


class FeedbackCrudServices:
    @classmethod
    def create(cls, user: User, input_data: dict) -> Feedback:
        obj = Feedback(
            business_area=BusinessArea.objects.get(slug=input_data["business_area_slug"]),
            issue_type=input_data["issue_type"],
        )

        obj.save()
        return obj
