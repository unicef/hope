import logging

from django.conf import settings
from django.contrib.auth import get_user_model

from social_core.exceptions import InvalidEmail
from social_core.pipeline import social_auth
from social_core.pipeline import user as social_core_user

from hct_mis_api.apps.account.microsoft_graph import MicrosoftGraphAPI
from hct_mis_api.apps.account.models import ACTIVE, Role, UserRole
from hct_mis_api.apps.core.models import BusinessArea

logger = logging.getLogger(__name__)


def social_details(backend, details, response, *args, **kwargs):
    logger.debug(f"social_details response:\n{response}")
    logger.debug(f"user_data:\n{backend.user_data(None, response=response)}")
    r = social_auth.social_details(backend, details, response, *args, **kwargs)

    if not r["details"].get("email"):
        user_data = backend.user_data(None, response=response) or {}
        r["details"]["email"] = user_data.get("email", user_data.get("signInNames.emailAddress"))

    r["details"]["idp"] = response.get("idp", "")
    return r


def user_details(strategy, details, backend, user=None, *args, **kwargs):
    logger.debug(f"user_details for user {user} details:\n{details}")
    # social_core_user.user_details use details dict to override some fields on User instance
    # in order to prevent it setting first and last name fields to empty values (which seems we always get from api)
    # we set them to current user values
    if user:
        # Prevents setting name back to empty but also gives an option to update the name if it had changed
        if not details.get("first_name"):
            details["first_name"] = user.first_name
        if not details.get("last_name"):
            details["last_name"] = user.last_name
        user.username = details["email"]
        user.status = ACTIVE
        user.save()

    return social_core_user.user_details(strategy, details, backend, user, *args, **kwargs)


def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if user and user.email:
        return
    elif is_new and not details.get("email"):
        logger.error("Email couldn't be validated")
        raise InvalidEmail(strategy)


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {"is_new": False}

    user = get_user_model().objects.create(
        email=details["email"],
        username=details["email"],
        first_name=details.get("first_name"),
        last_name=details.get("last_name"),
        status=ACTIVE,
    )
    ms_graph = MicrosoftGraphAPI()
    user_data = ms_graph.get_user_data(email=details["email"])
    business_area_code = user_data.get("extension_f4805b4021f643d0aa596e1367d432f1_unicefBusinessAreaCode")
    job_title = user_data.get("jobTitle")
    if job_title is not None:
        user.job_title = job_title
    user.set_unusable_password()
    user.save()
    if business_area_code:
        basic_user_role = UserRole()
        basic_user_role.role = Role.objects.filter(name="Basic User").first()
        basic_user_role.business_area = BusinessArea.objects.get(code=business_area_code)
        basic_user_role.user = user
        basic_user_role.save()

    return {"is_new": True, "user": user}


def create_admin(strategy, details, backend, user=None, is_new=False, *args, **kwargs):
    if user.email in settings.SUPERVISORS and is_new:
        user.is_staff = True
        user.is_superuser = True
        user.save()
