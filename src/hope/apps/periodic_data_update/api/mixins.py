from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.request import Request

from hope.apps.periodic_data_update.models import PDUOnlineEdit


class PDUOnlineEditAuthorizedUserMixin:
    """Provide an authorization check for the requesting user.

    Ensures the user is in the `authorized_users` list of the PDUOnlineEdit instance.
    If the action is a 'detail=False', it checks all instances specified in the 'ids' field of the request data.
    """

    def check_user_authorization(self, request: Request) -> None:
        user = request.user
        if not user or not user.is_authenticated:
            return

        if self.detail:
            instance = self.get_object()
            if not instance.authorized_users.filter(pk=user.pk).exists():
                raise PermissionDenied("You are not an authorized user for this PDU online edit.")
        else:
            ids = request.data.get("ids")
            if ids:
                queryset = PDUOnlineEdit.objects.filter(pk__in=ids)
                if queryset.count() != len(ids):
                    raise ValidationError("One or more PDU online edits not found.")

                queryset_unauthorized = queryset.exclude(authorized_users__pk=user.pk)
                if queryset_unauthorized.exists():
                    unauthorized_ids = ", ".join(
                        str(unauthorized_id) for unauthorized_id in queryset_unauthorized.values_list("id", flat=True)
                    )
                    raise PermissionDenied(f"You are not an authorized user for PDU Online Edit: {unauthorized_ids}")
