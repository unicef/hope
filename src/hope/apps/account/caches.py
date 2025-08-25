from typing import Optional


def get_user_permissions_version_key(user: "User") -> str:
    return f"user:{str(user.id)}:version"


def get_user_permissions_cache_key(
    user: "User",
    user_version: int,
    business_area: Optional["BusinessArea"],
    program: Optional["Program"],
) -> str:
    return f"permissions:{str(user.id)}:{user_version}:{business_area.slug if business_area else 'None'}:{program.id if program else 'None'}"
