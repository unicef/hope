# from rest_framework import serializers
# from rest_framework.generics import ListAPIView
#
# from hct_mis_api.aurora.models import AuroraRegistration
#
#
# class RegistrationDetailSerializer(serializers.ModelSerializer):
#     id = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name="registration-detail")
#     project = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name="project-detail")
#     records = serializers.SerializerMethodField()
#
#     class Meta:
#         model = AuroraRegistration
#         exclude = ("public_key",)
#
#     def get_default_field_names(self, declared_fields, model_info):
#         return (
#             [model_info.pk.name] + list(declared_fields) + list(model_info.fields) + list(model_info.forward_relations)
#         )
#
#     def get_records(self, obj):
#         req = self.context["request"]
#         return req.build_absolute_uri(reverse("api:registration-records", kwargs={"pk": obj.pk}))
#
#
# class RegistrationList(ListAPIView):
#     queryset = AuroraRegistration.objects.all()
#
#     def get_serializer_class(self):
#         return RegistrationListSerializer
#
#     def get_permissions(self):
#         return [permission() for permission in self.permission_classes]
#
#     @action(detail=True, permission_classes=[AllowAny])
#     def metadata(self, request, pk=None):
#         reg: Registration = self.get_object()
#         return Response(reg.metadata)
#
#     @action(detail=True, permission_classes=[AllowAny])
#     def version(self, request, slug=None):
#         reg: Registration = self.get_object()
#         return Response(
#             {
#                 "version": reg.version,
#                 "url": reg.get_absolute_url(),
#                 "auth": request.user.is_authenticated,
#                 "session_id": get_session_id(request),
#                 "active": reg.active,
#                 "protected": reg.protected,
#             }
#         )
#
#     @action(
#         detail=True,
#         methods=["GET"],
#         renderer_classes=[JSONRenderer],
#         pagination_class=RecordPageNumberPagination,
#         filter_backends=[DjangoFilterBackend],
#     )
#     def records(self, request, pk=None):
#         obj: Registration = self.get_object()
#         if not request.user.has_perm("registration.view_data", obj):
#             raise PermissionDenied()
#         self.res_etag = get_etag(
#             request,
#             str(obj.active),
#             str(obj.version),
#             os.environ.get("BUILD_DATE", ""),
#         )
#         response = get_conditional_response(request, str(self.res_etag))
#         if response is None:
#             queryset = (
#                 Record.objects.defer(
#                     "files",
#                     "storage",
#                 )
#                 .filter(registration__id=pk)
#                 .values()
#             )
#             flt = RecordFilter(request.GET, queryset=queryset)
#             if flt.form.is_valid():
#                 queryset = flt.filter_queryset(queryset)
#             page = self.paginate_queryset(queryset)
#
#             if page is None:
#                 serializer = DataTableRecordSerializer(
#                     queryset, many=True, context={"request": request}, metadata=obj.metadata
#                 )
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             else:
#                 serializer = DataTableRecordSerializer(
#                     page, many=True, context={"request": request}, metadata=obj.metadata
#                 )
#                 response = self.get_paginated_response(serializer.data)
#         response.headers.setdefault("ETag", self.res_etag)
#         response.headers.setdefault("Cache-Control", "private, max-age=120")
#         return response
