import abc

from django.contrib.auth import get_user_model
from django.db.models import Q

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.payment.models import CashPlan, PaymentVerification, PaymentRecord
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import TargetPopulation

User = get_user_model()


class HopeRedirect(abc.ABC):
    def __init__(
        self,
        user: User,
        ent: str,
        ca_id: str = "",
        source_id: str = "",
        program_id: str = "",
    ) -> None:
        self.user = user
        self.ent = ent
        self.ca_id = ca_id
        self.source_id = source_id.lower()
        self.program_id = program_id.lower()

    @abc.abstractmethod
    def url(self) -> str:
        pass

    def get_business_area_slug(self) -> str:
        if any([self.ca_id, self.source_id, self.program_id]):
            return self._get_business_area_slug_from_obj()
        return self._get_business_area_slug_from_user()

    @abc.abstractmethod
    def _get_business_area_slug_from_obj(self) -> str:
        pass

    def _get_business_area_slug_from_user(self) -> str:
        business_area = BusinessArea.objects.exclude(slug="global").filter(user_roles__user=self.user).first()
        if business_area:
            return business_area.slug
        return "/"


class HopeRedirectHousehold(HopeRedirect):
    def url(self) -> str:
        business_area_slug = self.get_business_area_slug()

        if not self.source_id:
            return f"/{business_area_slug}/population/household"
        return f"/{business_area_slug}/population/household/{encode_id_base64(self.source_id, 'Household')}"

    def _get_business_area_slug_from_obj(self) -> str:
        if household := Household.objects.filter(pk=self.source_id).first():
            return household.business_area.slug
        return "/"


class HopeRedirectIndividual(HopeRedirect):
    def url(self) -> str:
        business_area_slug = self.get_business_area_slug()

        if not self.source_id:
            return f"/{business_area_slug}/population/individuals"
        return f"/{business_area_slug}/population/individuals/{encode_id_base64(self.source_id, 'Individual')}"

    def _get_business_area_slug_from_obj(self) -> str:
        if individual := Individual.objects.filter(pk=self.source_id).first():
            return individual.business_area.slug
        return "/"


class HopeRedirectProgram(HopeRedirect):
    def url(self) -> str:
        business_area_slug = self.get_business_area_slug()

        if not self.source_id:
            return f"/{business_area_slug}/programs"
        return f"/{business_area_slug}/programs/{encode_id_base64(self.source_id, 'Program')}"

    def _get_business_area_slug_from_obj(self) -> str:
        if program := Program.objects.filter(pk=self.source_id).first():
            return program.business_area.slug
        return "/"


class HopeRedirectCashPlan(HopeRedirect):
    def url(self) -> str:
        business_area_slug = self.get_business_area_slug()

        if not self.program_id:
            return f"/{business_area_slug}/payment-verification"
        if cash_plan := self._get_cash_plan():
            return f"/{business_area_slug}/cashplans/{encode_id_base64(cash_plan.id, 'CashPlan')}"
        return "/"

    def _get_business_area_slug_from_obj(self) -> str:
        if cash_plan := self._get_cash_plan():
            return cash_plan.business_area.slug
        return "/"

    def _get_cash_plan(self) -> CashPlan:
        return CashPlan.objects.filter(Q(ca_id=self.ca_id) | Q(program__pk=self.program_id)).first()


class HopeRedirectPayment(HopeRedirect):
    def url(self) -> str:
        business_area_slug = self.get_business_area_slug()

        if not self.program_id:
            return f"/{business_area_slug}/payment-verification"
        payment_verification = self._get_payment_verification()
        return f"/{business_area_slug}/verification-records/{encode_id_base64(payment_verification.id, 'PaymentVerification')}"

    def _get_business_area_slug_from_obj(self) -> str:
        if payment_verification := self._get_payment_verification():
            return payment_verification.get_payment.business_area.slug
        return "/"

    def _get_payment_verification(self) -> PaymentVerification:
        return PaymentRecord.objects.filter(ca_id=self.ca_id).first().verification


class HopeRedirectTargetPopulation(HopeRedirect):
    def url(self) -> str:
        business_area_slug = self.get_business_area_slug()

        if not self.source_id:
            return f"/{business_area_slug}/target-population"
        return f"/{business_area_slug}/target-population/{encode_id_base64(self.source_id, 'TargetPopulation')}"

    def _get_business_area_slug_from_obj(self) -> str:
        if target_population := TargetPopulation.objects.filter(pk=self.source_id).first():
            return target_population.business_area.slug
        return "/"


class HopeRedirectDefault(HopeRedirect):
    def url(self) -> str:
        return "/"

    def _get_business_area_slug_from_obj(self) -> str:
        return ""


def get_hope_redirect(user: User, ent, ca_id="", source_id="", program_id="") -> HopeRedirect:
    if ent == "progres_registrationgroup":
        return HopeRedirectHousehold(user, ent, ca_id, source_id, program_id)
    if ent == "progres_individual":
        return HopeRedirectIndividual(user, ent, ca_id, source_id, program_id)
    if ent == "progres_program":
        return HopeRedirectProgram(user, ent, ca_id, source_id, program_id)
    if ent == "progres_cashplan":
        return HopeRedirectCashPlan(user, ent, ca_id, source_id, program_id)
    if ent == "progres_payment":
        return HopeRedirectPayment(user, ent, ca_id, source_id, program_id)
    if ent == "progres_targetpopulation":
        return HopeRedirectTargetPopulation(user, ent, ca_id, source_id, program_id)
    return HopeRedirectDefault(user, ent, ca_id, source_id, program_id)
