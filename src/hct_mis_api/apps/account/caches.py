from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from hct_mis_api.apps.account.models import User
    from hct_mis_api.apps.core.models import BusinessArea
    from hct_mis_api.apps.program.models import Program


def get_user_permissions_version_key(user: "User") -> str:
    return f"user:{str(user.id)}:version"


def get_user_permissions_cache_key(
    user: "User", user_version: int, business_area: Optional["BusinessArea"], program: Optional["Program"]
) -> str:
    return f"permissions:{str(user.id)}:{user_version}:{business_area.slug if business_area else 'None'}:{program.id if program else 'None'}"
