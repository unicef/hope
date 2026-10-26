from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING

from django.db import models
from django.http import Http404
from requests import HTTPError

from hope.apps.account.microsoft_graph import MicrosoftGraphAPI

if TYPE_CHECKING:
    from hope.models import User

logger = logging.getLogger(__name__)


class JobTitleSource(models.TextChoices):
    AD = "AD", "Active Directory"
    USER_RECORD = "USER_RECORD", "User record"


@dataclass(frozen=True)
class ActorSnapshot:
    name: str
    job_title: str
    job_title_source: str

    def as_model_fields(self, field: str) -> dict[str, str]:
        return {
            f"{field}_name": self.name,
            f"{field}_job_title": self.job_title,
            f"{field}_job_title_source": self.job_title_source,
        }

    def apply_to(self, record: models.Model, field: str) -> None:
        for name, value in self.as_model_fields(field).items():
            setattr(record, name, value)


def full_name(user: "User") -> str:
    return f"{user.first_name} {user.last_name}".strip()


def fetch_ad_job_title(ms_graph: MicrosoftGraphAPI, user: "User") -> str:
    # azure_id is only set for users imported through the admin; SSO-created users are found by e-mail.
    if user.azure_id:
        try:
            return ms_graph.get_user_data(uuid=str(user.azure_id)).get("jobTitle") or ""
        except (Http404, HTTPError):
            logger.info("AD user %s not found by azure_id, retrying by e-mail", user.pk)
    return ms_graph.get_user_data(email=user.email).get("jobTitle") or ""


def build_actor_snapshot(user: "User | None") -> ActorSnapshot:
    if user is None:
        return ActorSnapshot(name="", job_title="", job_title_source="")
    name = full_name(user)
    try:
        job_title = fetch_ad_job_title(MicrosoftGraphAPI(), user)
    except Http404:
        logger.info("User %s not found in AD, using the stored job title", user.pk)
        return ActorSnapshot(name=name, job_title=user.job_title, job_title_source=JobTitleSource.USER_RECORD)
    except Exception:  # noqa: BLE001 - MicrosoftGraphAPI raises bare Exception when the token request fails
        logger.warning("AD job title lookup failed for user %s, using the stored job title", user.pk, exc_info=True)
        return ActorSnapshot(name=name, job_title=user.job_title, job_title_source=JobTitleSource.USER_RECORD)
    return ActorSnapshot(name=name, job_title=job_title, job_title_source=JobTitleSource.AD)


def actor_display(record: models.Model, field: str) -> str:
    """Return "First Last (Job Title)" from the `<field>_name` / `<field>_job_title` columns stored on the record.

    Rows that have no stored snapshot values read the current values from the
    user record instead.
    """
    if getattr(record, f"{field}_job_title_source"):
        name = getattr(record, f"{field}_name")
        job_title = getattr(record, f"{field}_job_title")
    elif user := getattr(record, field):
        name = full_name(user)
        job_title = user.job_title
    else:
        return ""
    return name + (f" ({job_title})" if job_title else "")
