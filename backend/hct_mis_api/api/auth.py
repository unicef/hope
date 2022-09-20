from rest_framework.permissions import IsAuthenticated


class HOPEPermission(IsAuthenticated):
    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated):
            return request.user.user_roles.filter(role__permissions__contains=[view.permission]).exists()
        return False
