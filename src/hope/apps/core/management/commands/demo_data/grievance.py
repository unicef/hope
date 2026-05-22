from extras.test_utils.factories import GrievanceTicketFactory, TicketNeedsAdjudicationDetailsFactory
from hope.models import Area, Individual, Program, RegistrationDataImport


def generate_fake_grievances() -> None:
    program = Program.objects.get(name="Test Program")
    admin2 = Area.objects.filter(area_type__area_level=2).first()
    ind_qs = Individual.objects.filter(household__program=program)
    golden_records_individual = ind_qs[0]
    jan1 = ind_qs[1]
    jan2 = ind_qs[2]
    ba = program.business_area
    rdi = RegistrationDataImport.objects.filter(business_area=ba).first()
    grievance = GrievanceTicketFactory(
        unicef_id="GRV-0000001",
        status=1,
        category=8,
        issue_type=23,
        description="Test description",
        admin2=admin2,
        consent=True,
        business_area=ba,
        registration_data_import=rdi,
        extras={},
        ignored=False,
        household_unicef_id="HH-20-0000.0014",
    )
    grievance.programs.set([program])

    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance,
        golden_records_individual=golden_records_individual,
        is_multiple_duplicates_version=True,
        possible_duplicate=golden_records_individual,
        selected_individual=None,
        role_reassign_data={},
        extra_data={
            "golden_records": [
                {
                    "dob": "1923-01-01",
                    "score": 9.0,
                    "hit_id": str(jan1.pk),
                    "location": "Abband",
                    "full_name": "Jan Romaniak",
                    "proximity_to_score": 3.0,
                    "duplicate": False,
                    "distinct": False,
                }
            ],
            "possible_duplicate": [
                {
                    "dob": "1923-01-01",
                    "score": 9.0,
                    "hit_id": str(jan1.pk),
                    "location": "Abband",
                    "full_name": "Jan Romaniak1",
                    "proximity_to_score": 3.0,
                    "duplicate": True,
                    "distinct": False,
                },
                {
                    "dob": "1923-01-01",
                    "score": 9.0,
                    "hit_id": str(jan2.pk),
                    "location": "Abband",
                    "full_name": "Jan Romaniak2",
                    "proximity_to_score": 3.0,
                    "duplicate": False,
                    "distinct": True,
                },
            ],
        },
        score_min=9.0,
        score_max=9.0,
    )
    ticket_details.possible_duplicates.set([jan1, jan2])
    ticket_details.selected_individuals.set([jan2])
    ticket_details.selected_distinct.set([golden_records_individual])
