from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

from hope.config.env import env

CONSTANCE_REDIS_CONNECTION = env("CONSTANCE_REDIS_CONNECTION")
CONSTANCE_REDIS_CACHE_TIMEOUT = 1
CONSTANCE_ADDITIONAL_FIELDS = {
    "percentages": (
        "django.forms.fields.IntegerField",
        {
            "widget": "django.forms.widgets.NumberInput",
            "validators": [MinValueValidator(0), MaxValueValidator(100)],
        },
    ),
    "positive_integers": (
        "django.forms.fields.IntegerField",
        {
            "widget": "django.forms.widgets.NumberInput",
            "validators": [MinValueValidator(0)],
        },
    ),
    "positive_floats": (
        "django.forms.fields.FloatField",
        {
            "widget": "django.forms.widgets.NumberInput",
            "validators": [MinValueValidator(0)],
        },
    ),
    "priority_choices": (
        "django.forms.fields.ChoiceField",
        {
            "widget": "django.forms.Select",
            "choices": (
                (1, _("High")),
                (2, _("Medium")),
                (3, _("Low")),
            ),
        },
    ),
    "urgency_choices": (
        "django.forms.fields.ChoiceField",
        {
            "widget": "django.forms.Select",
            "choices": (
                (1, _("Very urgent")),
                (2, _("Urgent")),
                (3, _("Not urgent")),
            ),
        },
    ),
}

CONSTANCE_CONFIG = {
    # BATCH SETTINGS
    "AURORA_SERVER": (
        "",
        "",
        str,
    ),
    "DEDUPLICATION_DUPLICATE_SCORE": (
        6.0,
        "Results equal or above this score are considered duplicates",
        "positive_floats",
    ),
    "DEDUPLICATION_POSSIBLE_DUPLICATE_SCORE": (
        6.0,
        "Results equal or above this score are considered possible duplicates (needs adjudication) "
        "must be lower than DEDUPLICATION_DUPLICATE_SCORE",
        "positive_floats",
    ),
    "DEDUPLICATION_BATCH_DUPLICATES_PERCENTAGE": (
        50,
        "If percentage of duplicates is higher or equal to this setting, deduplication is aborted",
        "percentages",
    ),
    "PRODUCTION_SERVER": ("https://hope.unicef.org/api/admin", "", str),
    "KOBO_ADMIN_CREDENTIALS": (
        "",
        "Kobo superuser credentislas in format user:password",
        str,
    ),
    "DEDUPLICATION_BATCH_DUPLICATES_ALLOWED": (
        5,
        "If amount of duplicates for single individual exceeds this limit deduplication is aborted",
        "positive_integers",
    ),
    "KOBO_APP_API_TOKEN": ("", "Kobo KPI token", str),
    # GOLDEN RECORDS SETTINGS
    "DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_PERCENTAGE": (
        50,
        "If percentage of duplicates is higher or equal to this setting, deduplication is aborted",
        "percentages",
    ),
    "DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_ALLOWED": (
        5,
        "If amount of duplicates for single individual exceeds this limit deduplication is aborted",
        "positive_integers",
    ),
    # DEDUP ENGINE SETTINGS
    "BIOMETRIC_DEDUPLICATION_THRESHOLD": (
        0.0,
        "Results equal or above this score are considered duplicates",
        "percentages",
    ),
    # SANCTION LIST
    "SANCTION_LIST_MATCH_SCORE": (
        4.8,
        "Results equal or above this score are considered possible matches",
        "positive_floats",
    ),
    # RAPID PRO
    "RAPID_PRO_PROVIDER": ("tel", "Rapid pro messages provider (telegram/tel)"),
    # CASH ASSIST
    "CASH_ASSIST_URL_PREFIX": (
        "",
        "Cash Assist base url used to generate url to cash assist",
    ),
    "SEND_GRIEVANCES_NOTIFICATION": (
        False,
        "Should send grievances notification",
        bool,
    ),
    "SEND_PAYMENT_PLANS_NOTIFICATION": (
        False,
        "Should send payment plans notification",
        bool,
    ),
    "SEND_PDU_ONLINE_EDIT_NOTIFICATION": (
        False,
        "Should send PDU Online Edit notification",
        bool,
    ),
    "ENABLE_MAILJET": (
        False,
        "Enable sending emails via Mailjet",
        bool,
    ),
    "MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION": (
        0,
        "Mailjet template id for payment plan notification",
        int,
    ),
    "MAILJET_TEMPLATE_PDU_ONLINE_EDIT_NOTIFICATION": (
        0,
        "Mailjet template id for PDU Online Edit notification",
        int,
    ),
    "IGNORED_USER_LINKED_OBJECTS": (
        "created_advanced_filters,advancedfilter,logentry,social_auth,query,querylog,logs",
        "list of relation to hide in 'linked objects' user page",
        str,
    ),
    "QUICK_LINKS": (
        """Kobo,https://kobo-hope-trn.unitst.org/
Sentry,https://excubo.unicef.io/sentry/hct-mis-stg/
elasticsearch,hope-elasticsearch-coordinating-only:9200
Datamart,https://datamart.unicef.io
Flower,https://stg-hope.unitst.org/flower/
Azure,https://unicef.visualstudio.com/ICTD-HCT-MIS/
Clear Cache,clear-cache/
""",
        "",
        str,
    ),
    "USE_ELASTICSEARCH_FOR_INDIVIDUALS_SEARCH": (
        False,
        "Use elastic search for individuals search",
        bool,
    ),
    "USE_ELASTICSEARCH_FOR_HOUSEHOLDS_SEARCH": (
        False,
        "Use elastic search for households search",
        bool,
    ),
    "AUTO_MERGE_AFTER_AUTO_RDI_IMPORT": (
        False,
        "Automatically merge the population after server-triggered RDI import",
        bool,
    ),
    "RECALCULATE_POPULATION_FIELDS_CHUNK": (
        50000,
        "recalculate_population_fields_task Household table pagination value",
        "positive_integers",
    ),
    "PM_ACCEPTANCE_PROCESS_USER_HAVE_MULTIPLE_APPROVALS": (
        False,
        "The same user can have multiple approvals in acceptance process. "
        "Intended to be used only for testing purposes",
        bool,
    ),
    "REMOVE_RDI_LINKS_TIMEDELTA": (
        90,
        "The schedule (in days) which is applied to task remove_old_rdi_links_task",
        "positive_integers",
    ),
    "ADMIN_SYNC_REMOTE_SERVER": (
        "http://localhost:8000",
        "Remote server base URL",
        str,
    ),
    "ADMIN_SYNC_LOCAL_ADMIN_URL": ("/admin/", "Local server admin URL", str),
    "ADMIN_SYNC_REMOTE_ADMIN_URL": ("/admin/", "Remote server admin URL", str),
    "REST_BANNER_MESSAGE": ("", "Banner Message", str),
    "CLEARING_RECORD_FILES_TIMEDELTA": (
        60,
        "The schedule (in days) which is applied to task clean_old_record_files_task",
        "positive_integers",
    ),
    "SHOW_TOOLBAR": (False, "Show debug toolbar", bool),
    "REST_API_TTL": (
        60 * 60 * 24 * 7,  # 7 days
        "Time To Live for REST API cache",
        "positive_integers",
    ),
    "DEFAULT_BENEFICIARY_GROUP_NAME": (
        "Household",
        "Default Beneficiary Group name",
        str,
    ),
}

CONSTANCE_DBS = ("default",)
