import graphene
from django.core.exceptions import PermissionDenied
from graphene_django import DjangoObjectType

from account.models import User


class UserObjectType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ("password",)


class Query(graphene.ObjectType):
    me = graphene.Field(UserObjectType)


    def resolve_me(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise PermissionDenied("Permission Denied: User is not authenticated.")
        return info.context.user
