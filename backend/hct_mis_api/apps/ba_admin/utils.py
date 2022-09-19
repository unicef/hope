from hct_mis_api.apps.core.models import BusinessArea


def ba_for_user(user):
    if user.is_authenticated:
        return BusinessArea.objects.filter(user_roles__user=user)
