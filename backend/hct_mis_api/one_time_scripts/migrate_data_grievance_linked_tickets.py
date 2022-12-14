from django.core.paginator import Paginator

from hct_mis_api.apps.grievance.models import GrievanceTicketThrough


def populate_symmetrical_relation_objects() -> None:
    queryset = GrievanceTicketThrough.objects.all().order_by("pk")
    paginator = Paginator(queryset, 10000)
    queryset_count = queryset.count()
    for page_number in paginator.page_range:
        to_create = []
        print(f"Processing page {page_number}/{queryset_count/10000}")
        page = paginator.page(page_number)
        for gtt in page.object_list:
            to_create.append(
                GrievanceTicketThrough(
                    main_ticket=gtt.linked_ticket,
                    linked_ticket=gtt.main_ticket,
                )
            )

        GrievanceTicketThrough.objects.bulk_create(to_create, ignore_conflicts=True)
