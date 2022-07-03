from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from collections import defaultdict


class Command(BaseCommand):
    help = "Create Groups for setup permissions in django admin page"

    def handle(self, *args, **options):
        print("Starting create/update Groups...")
        actions = ["view", "add", "change", "delete"]
        app_model_map = {
            "account": ["incompatibleroles", "partner", "role", "userrole", "user"],
            "activity_log": ["logentry"],
            # "advanced_filters": ["advancedfilter"],  # change only
            # "constance": ["config"],  # change only
            "auth": ["group"],
            "django_celery_results": ["groupresult", "taskresult"],
            "core": [
                "adminarealevel",
                "adminarea",
                "businessarea",
                "countrycodemap",
                "flexibleattributechoice",
                "flexibleattributegroup",
                "flexibleattribute",
                "xlsxkobotemplate",
            ],
            "depot": ["storedfilter"],
            "geo": ["areatype", "area", "country"],
            "grievance": [
                "grievanceticket",
                "ticketaddindividualdetails",
                "ticketcomplaintdetails",
                "ticketdeletehouseholddetails",
                "ticketdeleteindividualdetails",
                "tickethouseholddataupdatedetails",
                "ticketindividualdataupdatedetails",
                "ticketneedsadjudicationdetails",
                "ticketnegativefeedbackdetails",
                "ticketnote",
                "ticketpaymentverificationdetails",
                "ticketpositivefeedbackdetails",
                "ticketreferraldetails",
                "ticketreferraldetails",
            ],
            "household": [
                "agency",
                "documenttype",
                "document",
                "entitlementcard",
                "household",
                "individualidentity",
                "individualroleinhousehold",
                "individual",
                "xlsxupdatefile",
            ],
            "cash_assist_datahub": [
                "cashplan",
                "paymentrecord",
                "programme",
                "serviceprovider",
                "session",
                "targetpopulation",
            ],
            "erp_datahub": ["downpayment", "fundscommitment"],
            "registration_datahub": [
                "diiahousehold",
                "diiaindividual",
                "importdata",
                "importedindividualidentity",
                "importeddocumenttype",
                "importeddocument",
                "importedhousehold",
                "importedindividualroleinhousehold",
                "importedindividual",
                "koboimportedsubmission",
                "record",
                "registrationdataimportdatahub",
            ],  # 'record' change only
            "mis_datahub": [
                "document",
                "downpayment",
                "fundscommitment",
                "household",
                "individualroleinhousehold",
                "individual",
                "program",
                "session",
                "targetpopulationentry",
                "targetpopulation",
            ],
            "payment": ["cashplanpaymentverification", "paymentrecord", "paymentverification", "serviceprovider"],
            "django_celery_beat": [
                "clockedschedule",
                "crontabschedule",
                "intervalschedule",
                "periodictask",
                "solarschedule",
            ],
            # "power_query": ["formatter", "query", "report"],  # 'dataset' change only
            "program": ["cashplan", "program"],
            "social_django": ["association", "nonce", "usersocialauth"],
            "registration_data": ["registrationdataimport"],
            "reporting": ["dashboardreport", "report"],
            "sanction_list": ["sanctionlistindividualdocument", "sanctionlistindividual"],
            "explorer": ["query"],
            "steficon": ["rulecommit"],  # 'rule' view only
            "targeting": ["householdselection", "targetpopulation"],
        }
        general_groups_map = {
            "view": "All Models Can VIEW",
            "add": "All Models Can ADD",
            "change": "All Models Can CHANGE",
            "delete": "All Models Can DELETE",
        }

        view_perms, add_perms, change_perms, delete_perms = list(), list(), list(), list()
        perms_list_map = defaultdict(list)
        perms_list_map.update({"view": view_perms, "add": add_perms, "change": change_perms, "delete": delete_perms})

        for action in actions:
            for app, models in app_model_map.items():
                for model in models:

                    ct = ContentType.objects.filter(app_label=app, model=model).first()

                    if not ct:
                        print(f"Not found ContentType for {app} {model}")
                        continue

                    perm_codename = action + "_" + model
                    perm = ct.permission_set.filter(codename=perm_codename).first()
                    if not perm:
                        print(f"Not found Permission with codename {perm_codename}")
                        continue

                    # use in general groups
                    perms_list_map.get(action).append(perm)

                    group_name = f"{ct.app_labeled_name} | Can {action} {ct.name}"
                    group, _ = Group.objects.get_or_create(name=group_name)
                    group.permissions.set([perm])

            # create general groups
            group, _ = Group.objects.get_or_create(name=general_groups_map.get(action))
            group.permissions.set(perms_list_map.get(action))

        self.stdout.write(self.style.SUCCESS("Successfully created/updated all Groups"))
