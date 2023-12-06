from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.payment.models import Payment, PaymentVerification


def get_object(program_id: str, url: str):
    module, name, encoded_id = url.split("/")[-3:]
    model = None
    lookup = None

    if module == "population":
        if name == "household":
            model = Household
            lookup = "program_id"
        else:
            model = Individual
            lookup = "program_id"
    elif module == "tickets" and name in ("user-generated", "system-generated"):
        model = GrievanceTicket
    elif module == "grievance" and name == "feedback":
        model = Feedback
        lookup = "household__program_id"
    elif module == "payment-module" and name == "payment":
        model = Payment
        lookup = "household__program_id"
    elif module == "verification" and name == "payment":
        model = PaymentVerification
        lookup = "payment_object__household__program_id"

    if model:
        obj = model.objects.get(id=decode_id_string(encoded_id))
        if getattr(obj, lookup) != program_id:
            return False

    return True

