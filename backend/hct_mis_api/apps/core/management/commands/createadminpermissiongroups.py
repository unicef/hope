from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from collections import defaultdict


class Command(BaseCommand):
    help = "Create Groups for setup permissions in django admin page"

    def create_group_and_set_permissions(self, group_name: str, perms: list):
        group, _ = Group.objects.get_or_create(name=group_name)
        group.permissions.set(perms)

    def _create_custom_group(self, codename, action, group_name):
        perm = Permission.objects.filter(codename=codename).first()
        if perm:
            self.create_group_and_set_permissions(group_name, [perm])
            self.perms_list_map.get(action).append(perm)
        else:
            print(f"Not found Permission with codename {codename}")

    def handle(self, *args, **options):
        print("Starting create/update Groups...")
        actions = ("view", "add", "change", "delete")
        app_model_map = {
            "account": ["incompatibleroles", "partner", "role", "userrole", "user"],
            "activity_log": ["logentry"],
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
            ],
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
            "power_query": ["formatter", "query", "report"],  # 'dataset' change only
            "program": ["cashplan", "program"],
            "social_django": ["association", "nonce", "usersocialauth"],
            "registration_data": ["registrationdataimport"],
            "reporting": ["dashboardreport", "report"],
            "sanction_list": ["sanctionlistindividualdocument", "sanctionlistindividual"],
            "explorer": ["query"],
            "steficon": ["rulecommit"],  # 'rule' view only
            "targeting": ["householdselection", "targetpopulation"],
            # "advanced_filters": ["advancedfilter"],  # change only
            # "constance": ["config"],  # change only
        }
        general_groups_map = {
            "view": "All Models Can VIEW",
            "add": "All Models Can ADD",
            "change": "All Models Can CHANGE",
            "delete": "All Models Can DELETE",
        }

        self.view_perms, self.add_perms, self.change_perms, self.delete_perms = list(), list(), list(), list()
        self.perms_list_map = defaultdict(list)
        self.perms_list_map.update(
            {"view": self.view_perms, "add": self.add_perms, "change": self.change_perms, "delete": self.delete_perms}
        )

        for app, models in app_model_map.items():
            for model in models:
                ct = ContentType.objects.filter(app_label=app, model=model).first()

                if not ct:
                    print(f"Not found ContentType for {app} {model}")
                    continue

                for action in actions:
                    perm_codename = action + "_" + model
                    perm = ct.permission_set.filter(codename=perm_codename).first()
                    if not perm:
                        print(f"Not found Permission with codename {perm_codename}")
                        continue

                    self.create_group_and_set_permissions(f"{ct.app_labeled_name} | Can {action} {ct.name}", [perm])
                    # use in general groups
                    self.perms_list_map.get(action).append(perm)

                # create groups for custom perms
                model_obj_perms = ct.model_class()._meta.permissions
                for codename, name in model_obj_perms:
                    perm = Permission.objects.filter(codename=codename).first()
                    if not perm:
                        print(f"Not found Permission with codename {codename}")
                        continue

                    self.create_group_and_set_permissions(f"{ct.app_labeled_name} | {name}", [perm])

        # custom create groups for Steficon Rule, Constance Config, Advanced Filter and Query Dataset
        other_custom_groups_map = [
            {"name": "steficon | Rule | Can view Rule", "codename": "view_rule", "action": "view"},
            {"name": "constance | config | Can change Config", "codename": "change_config", "action": "change"},
            {
                "name": "advanced_filters | Advanced Filter | Can change Advanced Filter",
                "codename": "change_advancedfilter",
                "action": "change",
            },
            {"name": "power_query | dataset | Can change dataset", "codename": "change_dataset", "action": "change"},
        ]

        for i in other_custom_groups_map:
            self._create_custom_group(i.get("codename", ""), i.get("action", ""), i.get("name", ""))

        # create general groups like can view all, can change all, can add all
        for action in actions:
            self.create_group_and_set_permissions(general_groups_map.get(action), self.perms_list_map.get(action))

        self.stdout.write(self.style.SUCCESS("Successfully created/updated all Groups"))
