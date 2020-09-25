import logging

from django.contrib.auth import get_user_model
from social_core.exceptions import InvalidEmail
from social_core.pipeline import social_auth
from social_core.pipeline import user as social_core_user

from account.models import UserRole, Role
from core.models import BusinessArea

logger = logging.getLogger("console")


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
    if user:
        user.first_name = details.get("first_name")
        user.last_name = details.get("last_name")
        user.username = details["email"]
        user.save()

    return social_core_user.user_details(strategy, details, backend, user, *args, **kwargs)


def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if user and user.email:
        return
    elif is_new and not details.get("email"):
        raise InvalidEmail(strategy)


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {"is_new": False}

    fullname = details["fullname"].split(" ")

    user = get_user_model().objects.create(
        email=details["email"],
        username=details["email"],
        first_name=details.get("first_name"),
        last_name=details.get("last_name"),
    )
    guest_user_role_afghanistan = UserRole()
    guest_user_role_afghanistan.role = Role.objects.filter(name="Guest").first()
    guest_user_role_afghanistan.business_area = BusinessArea.objects.first()
    user.set_unusable_password()
    user.save()
    guest_user_role_afghanistan.user = user
    guest_user_role_afghanistan.save()

    return {"is_new": True, "user": user}
