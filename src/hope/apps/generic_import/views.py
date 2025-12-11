from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import DatabaseError, transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from hope.apps.account.permissions import Permissions
from hope.apps.generic_import.celery_tasks import process_generic_import_task
from hope.apps.generic_import.forms import GenericImportForm
from hope.models import ImportData, RegistrationDataImport


class GenericImportUploadView(LoginRequiredMixin, FormView):
    """View for uploading generic import files."""

    template_name = "generic_import/upload.html"
    form_class = GenericImportForm
    success_url = reverse_lazy("generic_import:generic-import")

    def get_form_kwargs(self):
        """Pass user to form for queryset filtering."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        """Check GENERIC_IMPORT_DATA permission before processing request.

        Note: This check is intentionally separate from form_valid() check.
        dispatch() verifies user can access ANY business area (view access gate),
        while form_valid() verifies permission for the SPECIFIC selected BA.
        """
        # Only check permissions if user is authenticated
        # LoginRequiredMixin will handle redirect for unauthenticated users
        if request.user.is_authenticated:
            business_areas = request.user.business_areas

            if not business_areas.exists():
                raise PermissionDenied("You do not have access to any business area.")

            # Check GENERIC_IMPORT_DATA permission for at least one business area
            has_permission = any(
                request.user.has_perm(Permissions.GENERIC_IMPORT_DATA.name, ba) for ba in business_areas
            )

            if not has_permission:
                raise PermissionDenied(
                    "You do not have permission to import data. Required permission: GENERIC_IMPORT_DATA"
                )

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: GenericImportForm) -> HttpResponse:
        """Process valid form and trigger import task."""
        business_area = form.cleaned_data["business_area"]
        program = form.cleaned_data["program"]
        uploaded_file = form.cleaned_data["file"]

        # Verify user has permission for selected BA
        if not self.request.user.has_perm(Permissions.GENERIC_IMPORT_DATA.name, business_area):
            messages.error(
                self.request,
                f"You do not have permission to import data for {business_area.name}.",
            )
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                # Create ImportData instance
                import_data = ImportData.objects.create(
                    status=ImportData.STATUS_PENDING,
                    business_area_slug=business_area.slug,
                    data_type=ImportData.XLSX,
                    file=uploaded_file,
                    created_by_id=self.request.user.id,
                )

                # Create RegistrationDataImport instance
                # Generate unique name
                import_name = (
                    f"Generic Import {business_area.slug} - "
                    f"{program.name} - {import_data.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )

                rdi = RegistrationDataImport.objects.create(
                    name=import_name,
                    status=RegistrationDataImport.IMPORT_SCHEDULED,
                    business_area=business_area,
                    program=program,
                    imported_by=self.request.user,
                    data_source=RegistrationDataImport.XLS,
                    import_data=import_data,
                    number_of_individuals=0,
                    number_of_households=0,
                )

            # Trigger Celery task after transaction commits
            transaction.on_commit(
                lambda: process_generic_import_task.delay(
                    registration_data_import_id=str(rdi.id),
                    import_data_id=str(import_data.id),
                )
            )

            messages.success(
                self.request,
                f"File '{uploaded_file.name}' has been uploaded successfully. "
                f"Import '{import_name}' is being processed in the background.",
            )

        except (DatabaseError, ValidationError, ValueError) as e:
            messages.error(
                self.request,
                f"Failed to upload file: {str(e)}",
            )
            return self.form_invalid(form)

        return super().form_valid(form)

    def form_invalid(self, form: GenericImportForm) -> HttpResponse:
        """Handle invalid form submission."""
        # Display form errors
        for field, errors in form.errors.items():
            for error in errors:
                if field == "__all__":
                    messages.error(self.request, error)
                else:
                    messages.error(self.request, f"{field}: {error}")

        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Add extra context to template."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Generic Import"
        context["business_areas"] = self.request.user.business_areas
        return context
