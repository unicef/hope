from extras.test_utils.factories import BusinessAreaFactory, OrganizationFactory, ProjectFactory, RegistrationFactory
from hope.models import Program


def generate_aurora_test_data() -> None:
    program = Program.objects.get(name="Test Program")
    ukr_org = OrganizationFactory(
        source_id=1,
        name="organization_ukraine",
        slug="ukraine",
        business_area=BusinessAreaFactory(name="Ukraine"),
    )

    czech_org = OrganizationFactory(
        source_id=1,
        name="organization_czech_republic",
        slug="czech-republic",
        business_area=BusinessAreaFactory(name="Czechia"),
    )
    sri_lanka_org = OrganizationFactory(
        source_id=1,
        name="organization_sri_lanka",
        slug="sri-lanka",
        business_area=BusinessAreaFactory(name="Sri Lanka"),
    )
    ukr_project = ProjectFactory(source_id=2, organization=ukr_org, programme=program, name="project_ukraine")
    czech_project = ProjectFactory(
        source_id=2,
        organization=czech_org,
        programme=program,
        name="project_czech_republic",
    )
    sri_lanka_project = ProjectFactory(
        source_id=2,
        organization=sri_lanka_org,
        programme=program,
        name="project_sri_lanka",
    )
    RegistrationFactory(source_id=2, project=ukr_project, name="registration_ukraine", slug="ukraine")
    RegistrationFactory(
        source_id=2,
        project=czech_project,
        name="registration_czech_republic",
        slug="czech-republic",
    )
    RegistrationFactory(
        source_id=2,
        project=sri_lanka_project,
        name="registration_sri_lanka",
        slug="sri-lanka",
    )
