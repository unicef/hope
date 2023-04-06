import uuid
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.cash_assist_datahub.models import (
    CashPlan,
    PaymentRecord,
    Programme,
    ServiceProvider,
    Session,
    TargetPopulation,
)
from hct_mis_api.apps.household.models import FEMALE, MALE, Individual
from hct_mis_api.apps.payment.models import PaymentRecord as HopePaymentRecord
from hct_mis_api.apps.targeting.models import TargetPopulation as HopeTargetPopulation


@transaction.atomic
def populate_ca_datahub(targeting_id: str) -> None:
    target_population = HopeTargetPopulation.objects.get(id=targeting_id)
    print(f"HopeTargetPopulation {target_population}")

    session = Session.objects.create(
        business_area=target_population.business_area.cash_assist_code,
        status=Session.STATUS_READY,
    )
    print(f"Session {session}")

    tp = TargetPopulation.objects.create(
        session=session,
        ca_id=f"CA-{target_population.id}",
        ca_hash_id=uuid.uuid4(),
        mis_id=target_population.id,
    )
    print(f"TargetPopulation {tp}")

    program = Programme.objects.create(
        session=session,
        mis_id=target_population.program.id,
        ca_id=f"CA-{target_population.program.id}",
        ca_hash_id=uuid.uuid4(),
    )
    print(f"Programme {program}")

    sp = ServiceProvider.objects.create(
        session=session,
        business_area=target_population.business_area.cash_assist_code,
        ca_id=f"SP-{target_population.id}",
        full_name="SOME TEST BANK",
        short_name="STB",
        country="POL",
        vision_id=uuid.uuid4(),
    )
    print(f"ServiceProvider {sp}")

    cp = CashPlan.objects.create(
        session=session,
        business_area=target_population.business_area.cash_assist_code,
        cash_plan_id=f"123-CSH-12345-{target_population.id}",
        cash_plan_hash_id=uuid.uuid4(),
        status=CashPlan.DISTRIBUTION_COMPLETED,
        status_date=timezone.now(),
        name="Test CashAssist CashPlan",
        distribution_level="Test Distribution Level",
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=10),
        dispersion_date=timezone.now() + timedelta(days=2),
        coverage_duration=4,
        coverage_unit="days",
        comments="Test Comment",
        program_mis_id=target_population.program.id,
        delivery_type="TRANSFER",
        assistance_measurement="TEST measurement",
        assistance_through=sp.ca_id,
        vision_id=uuid.uuid4(),
        funds_commitment="123",
        validation_alerts_count=0,
        total_persons_covered=target_population.total_individuals_count,
        total_persons_covered_revised=target_population.total_individuals_count,
        payment_records_count=target_population.households.count(),
        total_entitled_quantity=10,
        total_entitled_quantity_revised=10,
        total_delivered_quantity=10,
        total_undelivered_quantity=0,
    )
    print(f"CashPlan {cp}")

    prs = []
    for hh in target_population.households.all():
        delta18 = relativedelta(years=+18)
        date18ago = datetime.now() - delta18

        targeted_individuals = Individual.objects.filter(household__id=hh.id).aggregate(
            male_children_count=Count("id", distinct=True, filter=Q(birth_date__gt=date18ago, sex=MALE)),
            female_children_count=Count("id", distinct=True, filter=Q(birth_date__gt=date18ago, sex=FEMALE)),
            male_adults_count=Count("id", distinct=True, filter=Q(birth_date__lte=date18ago, sex=MALE)),
            female_adults_count=Count("id", distinct=True, filter=Q(birth_date__lte=date18ago, sex=FEMALE)),
        )

        female_children_count = targeted_individuals.get("female_children_count", 0)
        male_children_count = targeted_individuals.get("male_children_count", 0)
        female_adults_count = targeted_individuals.get("female_adults_count", 0)
        male_adults_count = targeted_individuals.get("male_adults_count", 0)
        total_individuals_count = female_children_count + male_children_count + female_adults_count + male_adults_count

        prs.append(
            PaymentRecord(
                session=session,
                business_area=target_population.business_area.cash_assist_code,
                status=HopePaymentRecord.STATUS_SUCCESS,
                status_date=timezone.now(),
                ca_id=f"PR-{uuid.uuid4()}",
                ca_hash_id=uuid.uuid4(),
                cash_plan_ca_id=cp.cash_plan_id,
                registration_ca_id=uuid.uuid4(),
                household_mis_id=hh.id,
                head_of_household_mis_id=hh.head_of_household.id,
                full_name=hh.head_of_household.full_name,
                total_persons_covered=total_individuals_count,
                distribution_modality="Test distribution_modality",
                target_population_mis_id=target_population.id,
                target_population_cash_assist_id=tp.ca_id,
                entitlement_card_number="ASH12345678",
                entitlement_card_status=HopePaymentRecord.ENTITLEMENT_CARD_STATUS_ACTIVE,
                entitlement_card_issue_date=timezone.now() - timedelta(days=10),
                delivery_type=HopePaymentRecord.DELIVERY_TYPE_TRANSFER,
                currency="USD",
                entitlement_quantity=10,
                delivered_quantity=10,
                delivery_date=timezone.now() - timedelta(days=1),
                service_provider_ca_id=sp.ca_id,
                transaction_reference_id="12345",
                vision_id="random-pr-vision-id",
            )
        )
    PaymentRecord.objects.bulk_create(prs)
    print(f"PaymentRecords {len(prs)} {prs}")

    quantity = sum([pr.entitlement_quantity for pr in prs])

    cp.total_entitled_quantity = quantity
    cp.total_entitled_quantity_revised = quantity
    cp.total_delivered_quantity = quantity
    cp.save()
