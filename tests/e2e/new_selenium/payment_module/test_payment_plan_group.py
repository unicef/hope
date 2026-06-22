from decimal import Decimal
from unittest import mock

import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.factories import (
    DeliveryMechanismFactory,
    FileTempFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentFactory,
    PaymentHouseholdSnapshotFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    PaymentPlanSplitFactory,
)
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.apps.payment.xlsx.xlsx_payment_plan_group_delivery_export_service import (
    XlsxPaymentPlanGroupDeliveryExportService,
)
from hope.models import (
    BusinessArea,
    DeliveryMechanism,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    Payment,
    PaymentPlan,
    PaymentPlanGroup,
    ProgramCycle,
    User,
)

pytestmark = pytest.mark.django_db()


@pytest.fixture
def group_fsp() -> FinancialServiceProvider:
    return FinancialServiceProviderFactory(
        name="Group Delivery FSP",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        vision_vendor_number="900900900",
    )


@pytest.fixture
def group_delivery_mechanism() -> DeliveryMechanism:
    return DeliveryMechanismFactory(code="grp-cash", name="Group Cash", payment_gateway_id="grp-cash")


@pytest.fixture
def group_fsp_template(
    group_fsp: FinancialServiceProvider,
    group_delivery_mechanism: DeliveryMechanism,
) -> FinancialServiceProviderXlsxTemplate:
    return FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=group_fsp,
        delivery_mechanism=group_delivery_mechanism,
        xlsx_template=FinancialServiceProviderXlsxTemplateFactory(columns=["payment_id", "delivered_quantity"]),
    ).xlsx_template


@pytest.fixture
def exportable_group(
    program_cycle: ProgramCycle,
    group_fsp: FinancialServiceProvider,
    group_delivery_mechanism: DeliveryMechanism,
    group_fsp_template: FinancialServiceProviderXlsxTemplate,
) -> tuple[PaymentPlanGroup, Payment]:
    group = PaymentPlanGroupFactory(cycle=program_cycle, name="Exportable Group")
    plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=program_cycle.program.business_area,
        financial_service_provider=group_fsp,
        delivery_mechanism=group_delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
        plan_type=PaymentPlan.PlanType.REGULAR,
    )
    payment = PaymentFactory(
        parent=plan,
        financial_service_provider=group_fsp,
        delivery_type=group_delivery_mechanism,
        program=plan.program,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("10.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment, snapshot_data={})
    return group, payment


@pytest.fixture
def auth_code_template(business_area: BusinessArea) -> FinancialServiceProviderXlsxTemplate:
    # The export-with-auth-code dialog lists templates whose FSP is allowed in the business
    # area; this one carries the fsp_auth_code column so the dialog's auth-code path is exercised.
    fsp = FinancialServiceProviderFactory(
        name="Auth Code FSP",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        vision_vendor_number="900900902",
    )
    fsp.allowed_business_areas.add(business_area)
    return FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp,
        delivery_mechanism=DeliveryMechanismFactory(code="auth-cash", name="Auth Cash", payment_gateway_id="auth-cash"),
        xlsx_template=FinancialServiceProviderXlsxTemplateFactory(
            name="Auth Code Template",
            columns=["payment_id", "delivered_quantity", "fsp_auth_code"],
        ),
    ).xlsx_template


@pytest.fixture
def reconciliation_file(tmp_path, exportable_group: tuple[PaymentPlanGroup, Payment]) -> str:
    group, _ = exportable_group
    # Build the file from the real export service so its header matches exactly what the
    # import expects, then fill in a delivered_quantity for the single payment row.
    workbook = XlsxPaymentPlanGroupDeliveryExportService(group).generate_workbook()
    worksheet = workbook.active
    headers = [cell.value for cell in worksheet[1]]
    delivered_col = headers.index("delivered_quantity") + 1
    worksheet.cell(row=2, column=delivered_col).value = 50
    file_path = tmp_path / "reconciliation.xlsx"
    workbook.save(str(file_path))
    return str(file_path)


@pytest.fixture
def sendable_group(program_cycle: ProgramCycle) -> tuple[PaymentPlanGroup, PaymentPlan]:
    group = PaymentPlanGroupFactory(cycle=program_cycle, name="Sendable Group")
    plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=program_cycle.program.business_area,
        status=PaymentPlan.Status.ACCEPTED,
        financial_service_provider=FinancialServiceProviderFactory(name="PG FSP", vision_vendor_number="900900901"),
        use_payment_gateway=True,
    )
    PaymentPlanSplitFactory(payment_plan=plan)
    return group, plan


@pytest.fixture
def group_with_exported_batch(program_cycle: ProgramCycle) -> PaymentPlanGroup:
    group = PaymentPlanGroupFactory(cycle=program_cycle, name="Batch Group")
    PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=program_cycle.program.business_area,
        status=PaymentPlan.Status.ACCEPTED,
        export_tag=1,
        export_file_delivery=FileTempFactory(),
    )
    return group


@pytest.fixture
def group_with_unexported_batch(program_cycle: ProgramCycle) -> PaymentPlanGroup:
    group = PaymentPlanGroupFactory(cycle=program_cycle, name="Pending Batch Group")
    PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=program_cycle.program.business_area,
        status=PaymentPlan.Status.ACCEPTED,
        export_tag=1,
        export_file_delivery=None,
    )
    return group


def test_create_payment_plan_group(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    program_cycle: ProgramCycle,
) -> None:
    program = program_cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS,
        Permissions.PM_PAYMENT_PLAN_GROUP_CREATE,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/program-cycles")

        browser.click('[data-cy="program-cycle-title"] a')
        browser.wait_for_element_clickable('[data-cy="button-create-payment-plan-group"]')
        browser.click('[data-cy="button-create-payment-plan-group"]')

        browser.wait_for_element_visible('input[name="groupName"]')
        browser.type('input[name="groupName"]', "E2E Test Group")
        browser.click('[data-cy="button-create-group-submit"]')
        browser.wait_for_text("Payment Plan Group created")

        browser.click('[data-cy="nav-Payment Module"]')
        browser.wait_for_element_clickable('a[data-cy="nav-Groups"]')
        browser.click('a[data-cy="nav-Groups"]')

        browser.wait_for_text("E2E Test Group")


def test_edit_payment_plan_group(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    payment_plan_group: PaymentPlanGroup,
) -> None:
    program = payment_plan_group.cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
        Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{payment_plan_group.id}")

        browser.wait_for_element_clickable('[data-cy="button-edit-group-name"]')
        browser.click('[data-cy="button-edit-group-name"]')

        browser.wait_for_element_visible('input[name="name"]')
        browser.clear('input[name="name"]')
        browser.type('input[name="name"]', "Updated Group Name")
        browser.click('[data-cy="button-submit"]')

        browser.wait_for_text("Group name updated")
        browser.assert_text("Updated Group Name")


def test_delete_payment_plan_group(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    payment_plan_group: PaymentPlanGroup,
    second_payment_plan_group: PaymentPlanGroup,
) -> None:
    program = payment_plan_group.cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
        Permissions.PM_PAYMENT_PLAN_GROUP_DELETE,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{payment_plan_group.id}")

        browser.wait_for_element_clickable('[data-cy="button-delete-group"]')
        browser.click('[data-cy="button-delete-group"]')

        browser.wait_for_text("Are you sure you want to remove this Group?")
        browser.wait_for_element_clickable('[role="dialog"] [data-cy="button-submit"]')
        browser.find_element('[role="dialog"] [data-cy="button-submit"]').click()
        browser.wait_for_text("Group Deleted", timeout=20)

        browser.wait_for_text(second_payment_plan_group.name)
        browser.assert_text_not_visible(payment_plan_group.name)


def test_delete_button_hidden_when_group_has_payment_plans(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    group_with_payment_plan: PaymentPlanGroup,
) -> None:
    program = group_with_payment_plan.cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
        Permissions.PM_PAYMENT_PLAN_GROUP_DELETE,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(
            f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{group_with_payment_plan.id}"
        )

        browser.wait_for_element_visible('h5[data-cy="page-header-title"]')
        browser.assert_element_absent('[data-cy="button-delete-group"]')


def test_export_payment_plan_group(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    exportable_group: tuple[PaymentPlanGroup, Payment],
) -> None:
    group, _ = exportable_group
    program = group.cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
        Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{group.id}")

        browser.wait_for_element_clickable('[data-cy="button-delivery-export-xlsx-group"]')
        browser.click('[data-cy="button-delivery-export-xlsx-group"]')

        browser.wait_for_text("Export started")

        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{group.id}")
        browser.wait_for_text("Batch #1")
        browser.wait_for_element_visible('[data-cy="batch-download-link-1"]')


def test_export_payment_plan_group_with_auth_code(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    exportable_group: tuple[PaymentPlanGroup, Payment],
    auth_code_template: FinancialServiceProviderXlsxTemplate,
) -> None:
    group, _ = exportable_group
    program = group.cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
        Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX,
        Permissions.PM_EXPORT_XLSX_FOR_FSP,
        Permissions.PM_DOWNLOAD_FSP_AUTH_CODE,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{group.id}")

        browser.wait_for_element_clickable('[data-cy="button-delivery-export-xlsx-with-auth-code-group"]')
        browser.click('[data-cy="button-delivery-export-xlsx-with-auth-code-group"]')

        browser.wait_for_element_visible('[data-cy="dialog-delivery-export-xlsx-with-auth-code-group"]')
        template_input = browser.find_element('[data-cy="dialog-delivery-export-xlsx-with-auth-code-group"] input')
        template_input.click()
        template_input.send_keys("Auth Code Template")
        browser.select_listbox_element("Auth Code Template")

        browser.wait_for_element_clickable('[data-cy="button-delivery-export-xlsx-with-auth-code-group-submit"]')
        browser.click('[data-cy="button-delivery-export-xlsx-with-auth-code-group-submit"]')

        browser.wait_for_text("Export started")

        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{group.id}")
        browser.wait_for_text("Batch #1")
        browser.wait_for_element_visible('[data-cy="batch-download-link-1"]')


def test_import_payment_plan_group_reconciliation(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    exportable_group: tuple[PaymentPlanGroup, Payment],
    reconciliation_file: str,
) -> None:
    group, payment = exportable_group
    program = group.cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
        Permissions.PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{group.id}")

        browser.wait_for_element_clickable('[data-cy="button-delivery-import-xlsx-group"]')
        browser.click('[data-cy="button-delivery-import-xlsx-group"]')

        browser.wait_for_element_visible('[data-cy="dialog-delivery-import-xlsx-group"]')
        browser.choose_file('[data-cy="dialog-delivery-import-xlsx-group"] input[type="file"]', reconciliation_file)

        browser.wait_for_element_clickable('[data-cy="button-delivery-import-xlsx-group-submit"]')
        browser.click('[data-cy="button-delivery-import-xlsx-group-submit"]')

        browser.wait_for_text("Delivery reconciliation import started")

        payment.refresh_from_db()
        assert payment.delivered_quantity == Decimal("50.00")


def test_send_payment_plan_group_to_payment_gateway(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    sendable_group: tuple[PaymentPlanGroup, PaymentPlan],
) -> None:
    group, plan = sendable_group
    program = group.cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
        Permissions.PM_PAYMENT_PLAN_GROUP_SEND_TO_PAYMENT_GATEWAY,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{group.id}")

        browser.wait_for_element_clickable('[data-cy="button-send-to-payment-gateway-group"]')

        with mock.patch("hope.apps.payment.services.payment_plan_services.send_to_payment_gateway_async_task"):
            browser.click('[data-cy="button-send-to-payment-gateway-group"]')
            browser.wait_for_text("Sending to Payment Gateway started")

        plan.refresh_from_db()
        assert plan.background_action_status == PaymentPlan.BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY


def test_group_shows_batch_with_download_link(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    group_with_exported_batch: PaymentPlanGroup,
) -> None:
    group = group_with_exported_batch
    program = group.cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{group.id}")

        browser.wait_for_text("Batch #1")
        browser.wait_for_element_visible('[data-cy="batch-download-link-1"]')


def test_group_payment_plan_list_export_tag_links_to_batch(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    group_with_exported_batch: PaymentPlanGroup,
) -> None:
    group = group_with_exported_batch
    program = group.cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{group.id}")

        browser.wait_for_text("Export Batch")
        browser.wait_for_element_clickable(f'table a[href$="/groups/{group.id}/batches/1"]')
        browser.click(f'table a[href$="/groups/{group.id}/batches/1"]')

        browser.wait_for_element_visible('[data-cy="button-download-batch"]')


def test_batch_detail_shows_download_button_when_file_present(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    group_with_exported_batch: PaymentPlanGroup,
) -> None:
    group = group_with_exported_batch
    program = group.cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{group.id}/batches/1")

        browser.wait_for_element_visible('[data-cy="button-download-batch"]')
        browser.assert_element_absent('[data-cy="button-export-batch"]')


def test_batch_detail_shows_reexport_button_when_file_missing(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    group_with_unexported_batch: PaymentPlanGroup,
) -> None:
    group = group_with_unexported_batch
    program = group.cycle.program

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL,
    ):
        browser.login(username="noperm_user", password="testtest2")
        browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/groups/{group.id}/batches/1")

        browser.wait_for_element_visible('[data-cy="button-export-batch"]')
        browser.assert_element_absent('[data-cy="button-download-batch"]')
