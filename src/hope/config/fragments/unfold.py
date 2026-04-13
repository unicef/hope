from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

static_lazy = lazy(static, str)

UNFOLD = {
    "SITE_TITLE": "HOPE ADMIN",
    "SITE_HEADER": "HOPE Administration",
    "SITE_URL": "/",
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "type": "image/png",
            "href": static_lazy("administration/favicon-admin.png"),
        },
    ],
    "DASHBOARD_CALLBACK": "hope.apps.administration.admin_site.dashboard_callback",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "hope.config.fragments.unfold.environment_callback",
    "SITE_DROPDOWN": "hope.apps.administration.admin_site.site_dropdown_callback",
    "STYLES": [
        lambda request: static("admin/css/hope_admin.css"),
    ],
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Account"),
                "icon": "manage_accounts",
                "items": [
                    {
                        "title": _("Incompatible roles"),
                        "link": reverse_lazy("admin:account_incompatibleroles_changelist"),
                        "icon": "block",
                    },
                    {
                        "title": _("Partners"),
                        "link": reverse_lazy("admin:account_partner_changelist"),
                        "icon": "handshake",
                    },
                    {
                        "title": _("Role Assignments (Partner)"),
                        "link": reverse_lazy("admin:account_partnerroleassignment_changelist"),
                        "icon": "assignment",
                    },
                    {
                        "title": _("Role Assignments (User)"),
                        "link": reverse_lazy("admin:account_userroleassignment_changelist"),
                        "icon": "assignment_ind",
                    },
                    {
                        "title": _("Roles"),
                        "link": reverse_lazy("admin:account_role_changelist"),
                        "icon": "badge",
                    },
                    {
                        "title": _("User groups"),
                        "link": reverse_lazy("admin:account_usergroup_changelist"),
                        "icon": "group_work",
                    },
                    {
                        "title": _("Users"),
                        "link": reverse_lazy("admin:account_user_changelist"),
                        "icon": "person",
                    },
                ],
            },
            {
                "title": _("Accountability"),
                "icon": "verified",
                "items": [
                    {
                        "title": _("Feedbacks"),
                        "link": reverse_lazy("admin:accountability_feedback_changelist"),
                        "icon": "feedback",
                    },
                    {
                        "title": _("Messages"),
                        "link": reverse_lazy("admin:accountability_message_changelist"),
                        "icon": "message",
                    },
                    {
                        "title": _("Surveys"),
                        "link": reverse_lazy("admin:accountability_survey_changelist"),
                        "icon": "poll",
                    },
                ],
            },
            {
                "title": _("Activity Log"),
                "icon": "timeline",
                "items": [
                    {
                        "title": _("Log entries"),
                        "link": reverse_lazy("admin:activity_log_logentry_changelist"),
                        "icon": "history",
                    },
                ],
            },
            {
                "title": _("Advanced Filters"),
                "icon": "filter_alt",
                "items": [
                    {
                        "title": _("Advanced Filters"),
                        "link": reverse_lazy("admin:advanced_filters_advancedfilter_changelist"),
                        "icon": "filter_list",
                    },
                ],
            },
            {
                "title": _("API"),
                "icon": "api",
                "items": [
                    {
                        "title": _("Api Log Entries"),
                        "link": reverse_lazy("admin:api_apilogentry_changelist"),
                        "icon": "receipt_long",
                    },
                    {
                        "title": _("Api tokens"),
                        "link": reverse_lazy("admin:api_apitoken_changelist"),
                        "icon": "key",
                    },
                ],
            },
            {
                "title": _("Aurora"),
                "icon": "cloud",
                "items": [
                    {
                        "title": _("Organizations"),
                        "link": reverse_lazy("admin:aurora_organization_changelist"),
                        "icon": "corporate_fare",
                    },
                    {
                        "title": _("Projects"),
                        "link": reverse_lazy("admin:aurora_project_changelist"),
                        "icon": "folder_special",
                    },
                    {
                        "title": _("Records"),
                        "link": reverse_lazy("admin:aurora_record_changelist"),
                        "icon": "table_rows",
                    },
                    {
                        "title": _("Registrations"),
                        "link": reverse_lazy("admin:aurora_registration_changelist"),
                        "icon": "app_registration",
                    },
                ],
            },
            {
                "title": _("Authentication and Authorization"),
                "icon": "lock",
                "items": [
                    {
                        "title": _("Groups"),
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "icon": "group",
                    },
                    {
                        "title": _("Permissions"),
                        "link": reverse_lazy("admin:auth_permission_changelist"),
                        "icon": "security",
                    },
                ],
            },
            {
                "title": _("Celery Results"),
                "icon": "task_alt",
                "items": [
                    {
                        "title": _("Group results"),
                        "link": reverse_lazy("admin:django_celery_results_groupresult_changelist"),
                        "icon": "layers",
                    },
                    {
                        "title": _("Task results"),
                        "link": reverse_lazy("admin:django_celery_results_taskresult_changelist"),
                        "icon": "checklist",
                    },
                ],
            },
            {
                "title": _("Changelog"),
                "icon": "change_history",
                "items": [
                    {
                        "title": _("Changelogs"),
                        "link": reverse_lazy("admin:changelog_changelog_changelist"),
                        "icon": "history",
                    },
                ],
            },
            {
                "title": _("Constance"),
                "icon": "tune",
                "items": [
                    {
                        "title": _("Config"),
                        "link": reverse_lazy("admin:constance_config_changelist"),
                        "icon": "settings",
                    },
                ],
            },
            {
                "title": _("Content Types"),
                "icon": "category",
                "items": [
                    {
                        "title": _("Content types"),
                        "link": reverse_lazy("admin:contenttypes_contenttype_changelist"),
                        "icon": "label",
                    },
                ],
            },
            {
                "title": _("Core"),
                "icon": "settings",
                "items": [
                    {
                        "title": _("Asynchronous Jobs"),
                        "link": reverse_lazy("admin:core_asyncjob_changelist"),
                        "icon": "sync",
                    },
                    {
                        "title": _("Business areas"),
                        "link": reverse_lazy("admin:core_businessarea_changelist"),
                        "icon": "business",
                    },
                    {
                        "title": _("Country code maps"),
                        "link": reverse_lazy("admin:core_countrycodemap_changelist"),
                        "icon": "map",
                    },
                    {
                        "title": _("Data collecting types"),
                        "link": reverse_lazy("admin:core_datacollectingtype_changelist"),
                        "icon": "data_object",
                    },
                    {
                        "title": _("Flexible attribute choices"),
                        "link": reverse_lazy("admin:core_flexibleattributechoice_changelist"),
                        "icon": "checklist_rtl",
                    },
                    {
                        "title": _("Flexible attribute groups"),
                        "link": reverse_lazy("admin:core_flexibleattributegroup_changelist"),
                        "icon": "folder_open",
                    },
                    {
                        "title": _("Flexible attributes"),
                        "link": reverse_lazy("admin:core_flexibleattribute_changelist"),
                        "icon": "edit_note",
                    },
                    {
                        "title": _("Periodic Fields Data"),
                        "link": reverse_lazy("admin:core_periodicfielddata_changelist"),
                        "icon": "update",
                    },
                    {
                        "title": _("Xlsx kobo templates"),
                        "link": reverse_lazy("admin:core_xlsxkobotemplate_changelist"),
                        "icon": "description",
                    },
                ],
            },
            {
                "title": _("Depot"),
                "icon": "warehouse",
                "items": [
                    {
                        "title": _("Stored filters"),
                        "link": reverse_lazy("admin:depot_storedfilter_changelist"),
                        "icon": "save",
                    },
                ],
            },
            {
                "title": _("Django Flags"),
                "icon": "flag",
                "items": [
                    {
                        "title": _("Flag states"),
                        "link": reverse_lazy("admin:flags_flagstate_changelist"),
                        "icon": "toggle_on",
                    },
                ],
            },
            {
                "title": _("Geo"),
                "icon": "public",
                "items": [
                    {
                        "title": _("Area Types"),
                        "link": reverse_lazy("admin:geo_areatype_changelist"),
                        "icon": "layers",
                    },
                    {
                        "title": _("Areas"),
                        "link": reverse_lazy("admin:geo_area_changelist"),
                        "icon": "place",
                    },
                    {
                        "title": _("Countries"),
                        "link": reverse_lazy("admin:geo_country_changelist"),
                        "icon": "flag",
                    },
                ],
            },
            {
                "title": _("Grievance"),
                "icon": "report_problem",
                "items": [
                    {
                        "title": _("Grievance Tickets"),
                        "link": reverse_lazy("admin:grievance_grievanceticket_changelist"),
                        "icon": "confirmation_number",
                    },
                    {
                        "title": _("Grievance documents"),
                        "link": reverse_lazy("admin:grievance_grievancedocument_changelist"),
                        "icon": "attach_file",
                    },
                    {
                        "title": _("Ticket Add Individual Details"),
                        "link": reverse_lazy("admin:grievance_ticketaddindividualdetails_changelist"),
                        "icon": "person_add",
                    },
                    {
                        "title": _("Ticket Complaint Details"),
                        "link": reverse_lazy("admin:grievance_ticketcomplaintdetails_changelist"),
                        "icon": "report",
                    },
                    {
                        "title": _("Ticket Delete Household Details"),
                        "link": reverse_lazy("admin:grievance_ticketdeletehouseholddetails_changelist"),
                        "icon": "delete",
                    },
                    {
                        "title": _("Ticket Delete Individual Details"),
                        "link": reverse_lazy("admin:grievance_ticketdeleteindividualdetails_changelist"),
                        "icon": "person_remove",
                    },
                    {
                        "title": _("Ticket Household Data Update Details"),
                        "link": reverse_lazy("admin:grievance_tickethouseholddataupdatedetails_changelist"),
                        "icon": "home",
                    },
                    {
                        "title": _("Ticket Individual Data Update Details"),
                        "link": reverse_lazy("admin:grievance_ticketindividualdataupdatedetails_changelist"),
                        "icon": "manage_accounts",
                    },
                    {
                        "title": _("Ticket Needs Adjudication Details"),
                        "link": reverse_lazy("admin:grievance_ticketneedsadjudicationdetails_changelist"),
                        "icon": "gavel",
                    },
                    {
                        "title": _("Ticket Negative Feedback Details"),
                        "link": reverse_lazy("admin:grievance_ticketnegativefeedbackdetails_changelist"),
                        "icon": "thumb_down",
                    },
                    {
                        "title": _("Ticket Payment Verification Details"),
                        "link": reverse_lazy("admin:grievance_ticketpaymentverificationdetails_changelist"),
                        "icon": "fact_check",
                    },
                    {
                        "title": _("Ticket Positive Feedback Details"),
                        "link": reverse_lazy("admin:grievance_ticketpositivefeedbackdetails_changelist"),
                        "icon": "thumb_up",
                    },
                    {
                        "title": _("Ticket Referral Details"),
                        "link": reverse_lazy("admin:grievance_ticketreferraldetails_changelist"),
                        "icon": "forward",
                    },
                    {
                        "title": _("Ticket Sensitive Details"),
                        "link": reverse_lazy("admin:grievance_ticketsensitivedetails_changelist"),
                        "icon": "privacy_tip",
                    },
                    {
                        "title": _("Ticket notes"),
                        "link": reverse_lazy("admin:grievance_ticketnote_changelist"),
                        "icon": "sticky_note_2",
                    },
                ],
            },
            {
                "title": _("Household"),
                "icon": "home",
                "items": [
                    {
                        "title": _("Document types"),
                        "link": reverse_lazy("admin:household_documenttype_changelist"),
                        "icon": "article",
                    },
                    {
                        "title": _("Documents"),
                        "link": reverse_lazy("admin:household_document_changelist"),
                        "icon": "description",
                    },
                    {
                        "title": _("Entitlement cards"),
                        "link": reverse_lazy("admin:household_entitlementcard_changelist"),
                        "icon": "credit_card",
                    },
                    {
                        "title": _("Facilities"),
                        "link": reverse_lazy("admin:household_facility_changelist"),
                        "icon": "apartment",
                    },
                    {
                        "title": _("Household collections"),
                        "link": reverse_lazy("admin:household_householdcollection_changelist"),
                        "icon": "collections",
                    },
                    {
                        "title": _("Households"),
                        "link": reverse_lazy("admin:household_household_changelist"),
                        "icon": "group",
                    },
                    {
                        "title": _("Individual Identities"),
                        "link": reverse_lazy("admin:household_individualidentity_changelist"),
                        "icon": "badge",
                    },
                    {
                        "title": _("Individual collections"),
                        "link": reverse_lazy("admin:household_individualcollection_changelist"),
                        "icon": "people",
                    },
                    {
                        "title": _("Individual role in households"),
                        "link": reverse_lazy("admin:household_individualroleinhousehold_changelist"),
                        "icon": "supervisor_account",
                    },
                    {
                        "title": _("Individuals"),
                        "link": reverse_lazy("admin:household_individual_changelist"),
                        "icon": "person",
                    },
                    {
                        "title": _("Xlsx update files"),
                        "link": reverse_lazy("admin:household_xlsxupdatefile_changelist"),
                        "icon": "upload_file",
                    },
                ],
            },
            {
                "title": _("Payment"),
                "icon": "payments",
                "items": [
                    {
                        "title": _("Account types"),
                        "link": reverse_lazy("admin:payment_accounttype_changelist"),
                        "icon": "category",
                    },
                    {
                        "title": _("Accounts"),
                        "link": reverse_lazy("admin:payment_account_changelist"),
                        "icon": "account_balance_wallet",
                    },
                    {
                        "title": _("Delivery Mechanisms"),
                        "link": reverse_lazy("admin:payment_deliverymechanism_changelist"),
                        "icon": "local_shipping",
                    },
                    {
                        "title": _("Delivery mechanism configs"),
                        "link": reverse_lazy("admin:payment_deliverymechanismconfig_changelist"),
                        "icon": "settings",
                    },
                    {
                        "title": _("Financial institution mappings"),
                        "link": reverse_lazy("admin:payment_financialinstitutionmapping_changelist"),
                        "icon": "device_hub",
                    },
                    {
                        "title": _("Financial institutions"),
                        "link": reverse_lazy("admin:payment_financialinstitution_changelist"),
                        "icon": "account_balance",
                    },
                    {
                        "title": _("Financial service provider xlsx templates"),
                        "link": reverse_lazy("admin:payment_financialserviceproviderxlsxtemplate_changelist"),
                        "icon": "table_chart",
                    },
                    {
                        "title": _("Financial service providers"),
                        "link": reverse_lazy("admin:payment_financialserviceprovider_changelist"),
                        "icon": "storefront",
                    },
                    {
                        "title": _("Fsp xlsx template per delivery mechanisms"),
                        "link": reverse_lazy("admin:payment_fspxlsxtemplateperdeliverymechanism_changelist"),
                        "icon": "description",
                    },
                    {
                        "title": _("Payment Plans"),
                        "link": reverse_lazy("admin:payment_paymentplan_changelist"),
                        "icon": "receipt",
                    },
                    {
                        "title": _("Payment plan supporting documents"),
                        "link": reverse_lazy("admin:payment_paymentplansupportingdocument_changelist"),
                        "icon": "attach_file",
                    },
                    {
                        "title": _("Payment verification plans"),
                        "link": reverse_lazy("admin:payment_paymentverificationplan_changelist"),
                        "icon": "verified",
                    },
                    {
                        "title": _("Payment verifications"),
                        "link": reverse_lazy("admin:payment_paymentverification_changelist"),
                        "icon": "fact_check",
                    },
                    {
                        "title": _("Payments"),
                        "link": reverse_lazy("admin:payment_payment_changelist"),
                        "icon": "paid",
                    },
                    {
                        "title": _("Western Union Invoices"),
                        "link": reverse_lazy("admin:payment_westernunioninvoice_changelist"),
                        "icon": "request_quote",
                    },
                    {
                        "title": _("Western Union Payment Plan Reports"),
                        "link": reverse_lazy("admin:payment_westernunionpaymentplanreport_changelist"),
                        "icon": "summarize",
                    },
                ],
            },
            {
                "title": _("Periodic Tasks"),
                "icon": "schedule",
                "items": [
                    {
                        "title": _("Clocked"),
                        "link": reverse_lazy("admin:django_celery_beat_clockedschedule_changelist"),
                        "icon": "alarm",
                    },
                    {
                        "title": _("Crontabs"),
                        "link": reverse_lazy("admin:django_celery_beat_crontabschedule_changelist"),
                        "icon": "event_repeat",
                    },
                    {
                        "title": _("Intervals"),
                        "link": reverse_lazy("admin:django_celery_beat_intervalschedule_changelist"),
                        "icon": "timelapse",
                    },
                    {
                        "title": _("Periodic tasks"),
                        "link": reverse_lazy("admin:django_celery_beat_periodictask_changelist"),
                        "icon": "repeat",
                    },
                    {
                        "title": _("Solar events"),
                        "link": reverse_lazy("admin:django_celery_beat_solarschedule_changelist"),
                        "icon": "wb_sunny",
                    },
                ],
            },
            {
                "title": _("Periodic Data Update"),
                "icon": "update",
                "items": [
                    {
                        "title": _("Pdu online edits"),
                        "link": reverse_lazy("admin:periodic_data_update_pduonlineedit_changelist"),
                        "icon": "edit",
                    },
                    {
                        "title": _("Pdu xlsx templates"),
                        "link": reverse_lazy("admin:periodic_data_update_pduxlsxtemplate_changelist"),
                        "icon": "table_chart",
                    },
                    {
                        "title": _("Pdu xlsx uploads"),
                        "link": reverse_lazy("admin:periodic_data_update_pduxlsxupload_changelist"),
                        "icon": "upload_file",
                    },
                ],
            },
            {
                "title": _("Programme"),
                "icon": "folder",
                "items": [
                    {
                        "title": _("Beneficiary Groups"),
                        "link": reverse_lazy("admin:program_beneficiarygroup_changelist"),
                        "icon": "groups",
                    },
                    {
                        "title": _("Programme Cycles"),
                        "link": reverse_lazy("admin:program_programcycle_changelist"),
                        "icon": "loop",
                    },
                    {
                        "title": _("Programmes"),
                        "link": reverse_lazy("admin:program_program_changelist"),
                        "icon": "topic",
                    },
                ],
            },
            {
                "title": _("Python Social Auth"),
                "icon": "share",
                "items": [
                    {
                        "title": _("Associations"),
                        "link": reverse_lazy("admin:social_django_association_changelist"),
                        "icon": "link",
                    },
                    {
                        "title": _("Nonces"),
                        "link": reverse_lazy("admin:social_django_nonce_changelist"),
                        "icon": "password",
                    },
                    {
                        "title": _("User social auths"),
                        "link": reverse_lazy("admin:social_django_usersocialauth_changelist"),
                        "icon": "person",
                    },
                ],
            },
            {
                "title": _("Registration Data"),
                "icon": "upload_file",
                "items": [
                    {
                        "title": _("Deduplication engine similarity pairs"),
                        "link": reverse_lazy("admin:registration_data_deduplicationenginesimilaritypair_changelist"),
                        "icon": "content_copy",
                    },
                    {
                        "title": _("Import datas"),
                        "link": reverse_lazy("admin:registration_data_importdata_changelist"),
                        "icon": "import_export",
                    },
                    {
                        "title": _("Kobo import datas"),
                        "link": reverse_lazy("admin:registration_data_koboimportdata_changelist"),
                        "icon": "cloud_download",
                    },
                    {
                        "title": _("Registration data imports"),
                        "link": reverse_lazy("admin:registration_data_registrationdataimport_changelist"),
                        "icon": "table_rows",
                    },
                ],
            },
            {
                "title": _("Sanction List"),
                "icon": "gavel",
                "items": [
                    {
                        "title": _("Aliases"),
                        "link": reverse_lazy("admin:sanction_list_sanctionlistindividualaliasname_changelist"),
                        "icon": "badge",
                    },
                    {
                        "title": _("Birthdays"),
                        "link": reverse_lazy("admin:sanction_list_sanctionlistindividualdateofbirth_changelist"),
                        "icon": "cake",
                    },
                    {
                        "title": _("Documents"),
                        "link": reverse_lazy("admin:sanction_list_sanctionlistindividualdocument_changelist"),
                        "icon": "description",
                    },
                    {
                        "title": _("Individuals"),
                        "link": reverse_lazy("admin:sanction_list_sanctionlistindividual_changelist"),
                        "icon": "person",
                    },
                    {
                        "title": _("Nationalities"),
                        "link": reverse_lazy("admin:sanction_list_sanctionlistindividualnationalities_changelist"),
                        "icon": "flag",
                    },
                    {
                        "title": _("Sanction List Individual/Countries"),
                        "link": reverse_lazy("admin:sanction_list_sanctionlistindividualcountries_changelist"),
                        "icon": "public",
                    },
                    {
                        "title": _("Sanction lists"),
                        "link": reverse_lazy("admin:sanction_list_sanctionlist_changelist"),
                        "icon": "list",
                    },
                    {
                        "title": _("Uploaded xlsx files"),
                        "link": reverse_lazy("admin:sanction_list_uploadedxlsxfile_changelist"),
                        "icon": "upload_file",
                    },
                ],
            },
            {
                "title": _("Sites"),
                "icon": "language",
                "items": [
                    {
                        "title": _("Sites"),
                        "link": reverse_lazy("admin:sites_site_changelist"),
                        "icon": "web",
                    },
                ],
            },
            {
                "title": _("Smart Admin"),
                "icon": "admin_panel_settings",
                "items": [
                    {
                        "title": _("Log entries"),
                        "link": reverse_lazy("admin:admin_logentry_changelist"),
                        "icon": "history",
                    },
                ],
            },
            {
                "title": _("SQL Explorer"),
                "icon": "storage",
                "items": [
                    {
                        "title": _("Database connections"),
                        "link": reverse_lazy("admin:explorer_databaseconnection_changelist"),
                        "icon": "cable",
                    },
                    {
                        "title": _("Explorer values"),
                        "link": reverse_lazy("admin:explorer_explorervalue_changelist"),
                        "icon": "tune",
                    },
                    {
                        "title": _("Queries"),
                        "link": reverse_lazy("admin:explorer_query_changelist"),
                        "icon": "manage_search",
                    },
                ],
            },
            {
                "title": _("Steficon"),
                "icon": "code",
                "items": [
                    {
                        "title": _("Rule Commits"),
                        "link": reverse_lazy("admin:steficon_rulecommit_changelist"),
                        "icon": "commit",
                    },
                    {
                        "title": _("Rules"),
                        "link": reverse_lazy("admin:steficon_rule_changelist"),
                        "icon": "rule",
                    },
                ],
            },
            {
                "title": _("Universal Update Script"),
                "icon": "sync",
                "items": [
                    {
                        "title": _("Universal updates"),
                        "link": reverse_lazy(
                            "admin:universal_update_script_universalupdate_changelist"
                        ),
                        "icon": "update",
                    },
                ],
            },
            {
                "title": _("Vision"),
                "icon": "visibility",
                "items": [
                    {
                        "title": _("Down payments"),
                        "link": reverse_lazy("admin:vision_downpayment_changelist"),
                        "icon": "arrow_downward",
                    },
                    {
                        "title": _("Funds commitment items"),
                        "link": reverse_lazy("admin:vision_fundscommitmentitem_changelist"),
                        "icon": "receipt_long",
                    },
                    {
                        "title": _("Funds commitments"),
                        "link": reverse_lazy("admin:vision_fundscommitment_changelist"),
                        "icon": "handshake",
                    },
                ],
            },
        ],
    },
    "COLORS": {
        "primary": {
            "50": "#e3f2fd",
            "100": "#bbdefb",
            "200": "#90caf9",
            "300": "#64b5f6",
            "400": "#42a5f5",
            "500": "#00ADEF",
            "600": "#1e88e5",
            "700": "#1976d2",
            "800": "#1565c0",
            "900": "#0d47a1",
            "950": "#0a3a7e",
        },
    },
}


def environment_callback(request: object) -> tuple[str, str]:
    """Return environment name and color for the admin header banner."""
    host = request.get_host()
    url = request.build_absolute_uri()

    color_map = {
        "localhost": ("Local", "#FF6600"),
        "trn": ("Training", "#BF360C"),
        "stg": ("Staging", "#673AB7"),
        "dev": ("Development", "#00796B"),
        "eph": ("Ephemeral", "#CC00EF"),
        "tst": ("Test", "#EF00A7"),
    }

    if "localhost" in host:
        return color_map["localhost"]

    for env_key, (label, color) in color_map.items():
        if env_key in url:
            return label, color

    return "Production", "#00ADEF"
