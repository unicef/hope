from functools import partial
from typing import List, Tuple

from graphene.types.argument import to_arguments
from graphene_django import DjangoConnectionField
from graphene_django.filter.utils import get_filtering_args_from_filterset, get_filterset_class
from graphql import GraphQLError
from collections import OrderedDict
from model_utils import Choices

from core.models import BusinessArea

PERMISSION_CREATE = "CREATE"
PERMISSION_UPDATE = "UPDATE"
PERMISSION_DELETE = "DELETE"
PERMISSION_READ = "READ"
PERMISSION_LIST = "LIST"
PERMISSION_RUN = "RUN"


PERMISSION_DASHBOARD = "DASHBOARD"
PERMISSION_RDI_LIST = "RDI"

PERMISSION_RDI_IMPORT = "PERMISSION_RDI_IMPORT"
PERMISSION_RDI_RERUN_DEDUPLICATION = "PERMISSION_RDI_RERUN_DEDUPLICATION"
PERMISSION_RDI_MERGE = "PERMISSION_RDI_MERGE"
PERMISSION_RDI_KOBO = "PERMISSION_RDI_KOBO"
PERMISSION_RDI_XLSX = "PERMISSION_RDI_XLSX"
PERMISSION_PROGRAM = "PERMISSION_PROGRAM"
PERMISSIONS_DICT = {
    PERMISSION_DASHBOARD: [PERMISSION_READ],
    PERMISSION_RDI_LIST: [PERMISSION_READ],
    PERMISSION_RDI_IMPORT: [PERMISSION_CREATE, PERMISSION_READ],
    PERMISSION_RDI_MERGE: [PERMISSION_RUN],
    PERMISSION_RDI_RERUN_DEDUPLICATION: [PERMISSION_RUN],
    PERMISSION_RDI_KOBO: [PERMISSION_CREATE],
    PERMISSION_RDI_XLSX: [PERMISSION_CREATE],
    PERMISSION_PROGRAM: [PERMISSION_LIST, PERMISSION_READ, PERMISSION_CREATE, PERMISSION_UPDATE, PERMISSION_DELETE],
}

PERMISSIONS_CHOICES = [(f"{key}.{perm}", f"{key}.{perm}") for key, value in PERMISSIONS_DICT.items() for perm in value]

# Tribute to Akul Senior Software Developer, he was a cool guy
def dict_to_choices() -> List[Tuple[str, str]]:
    """Change dict to choices"""
    # declaring empty list for choices
    choices = []
    # iteration over keys and values in PERMISSIONS_DICT items
    for key, value in PERMISSIONS_DICT.items():
        # iteration over permissions in value list
        for perm in value:
            # adding key and value into tuple
            choices.append((f"{key}.{perm}", f"{key}.{perm}"))
    #  returning choices list
    return choices


class BasePermission:
    @classmethod
    def has_permission(cls, info, **kwargs):
        return False


class AllowAny(BasePermission):
    @classmethod
    def has_permission(cls, info, **kwargs):
        return True


class AllowAuthenticated(BasePermission):
    @classmethod
    def has_permission(cls, info, **kwargs):
        return info.context.user.is_authenticated


def hopePermissionClass(permission):
    class XDPerm(BasePermission):
        @classmethod
        def has_permission(cls, info, **kwargs):
            business_area_arg = kwargs.get("business_area")
            if isinstance(business_area_arg, BusinessArea):
                business_area = business_area_arg
            else:
                if business_area_arg is None:
                    return False
                business_area = BusinessArea.objects.filter(slug=business_area_arg).first()
                if business_area is None:
                    return False
            return info.context.user.has_permission(permission, business_area)

    return XDPerm


class BaseNodePermissionMixin:
    permission_classes = (AllowAny,)

    @classmethod
    def check_node_permission(cls, info, object_instance):
        business_area = object_instance.business_area
        if not all((perm.has_permission(info, business_area=business_area) for perm in cls.permission_classes)):
            raise GraphQLError("Permission Denied")

    @classmethod
    def get_node(cls, info, id):
        try:
            object_instance = cls._meta.model.objects.get(pk=id)  # type: ignore
            cls.check_node_permission(info, object_instance)
        except cls._meta.model.DoesNotExist:  # type: ignore
            object_instance = None
        return object_instance


class DjangoPermissionFilterConnectionField(DjangoConnectionField):
    def __init__(
        self,
        type,
        fields=None,
        order_by=None,
        extra_filter_meta=None,
        filterset_class=None,
        permission_classes=(AllowAny,),
        *args,
        **kwargs,
    ):
        self._fields = fields
        self._provided_filterset_class = filterset_class
        self._filterset_class = None
        self._extra_filter_meta = extra_filter_meta
        self._base_args = None
        self.permission_classes = permission_classes
        super(DjangoPermissionFilterConnectionField, self).__init__(type, *args, **kwargs)

    @property
    def args(self):
        return to_arguments(self._base_args or OrderedDict(), self.filtering_args)

    @args.setter
    def args(self, args):
        self._base_args = args

    @property
    def filterset_class(self):
        if not self._filterset_class:
            fields = self._fields or self.node_type._meta.filter_fields
            meta = dict(model=self.model, fields=fields)
            if self._extra_filter_meta:
                meta.update(self._extra_filter_meta)

            filterset_class = self._provided_filterset_class or (self.node_type._meta.filterset_class)
            self._filterset_class = get_filterset_class(filterset_class, **meta)

        return self._filterset_class

    @property
    def filtering_args(self):
        return get_filtering_args_from_filterset(self.filterset_class, self.node_type)

    @classmethod
    def resolve_queryset(cls, connection, iterable, info, args, filtering_args, filterset_class, permission_classes):
        filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
        if not all((perm.has_permission(info, **filter_kwargs) for perm in permission_classes)):
            raise GraphQLError("Permission Denied")
        qs = super(DjangoPermissionFilterConnectionField, cls).resolve_queryset(connection, iterable, info, args)
        return filterset_class(data=filter_kwargs, queryset=qs, request=info.context).qs

    def get_queryset_resolver(self):
        return partial(
            self.resolve_queryset,
            filterset_class=self.filterset_class,
            filtering_args=self.filtering_args,
            permission_classes=self.permission_classes,
        )
