import { AdminButton } from '@core/AdminButton';
import type { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { StatusBox } from '@core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import {
  paymentListBackgroundActionStatusToColor,
  paymentListStatusToColor,
} from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import type { PaymentPlanAcceptanceAction } from './actions/AcceptanceActionPaymentPlanButton';
import { AcceptanceActionPaymentPlanButton } from './actions/AcceptanceActionPaymentPlanButton';
import { AbortPaymentPlanButton } from './actions/AbortPaymentPlanButton';
import { ClosePaymentPlanButton } from './actions/ClosePaymentPlanButton';
import { CreateLinkedPaymentPlanButton } from './actions/CreateLinkedPaymentPlan';
import { DeletePaymentPlan } from './actions/DeletePaymentPlan';
import { EditPaymentPlan } from './actions/EditPaymentPlan';
import { DeliveryExportXlsxPaymentPlanButton } from './actions/DeliveryExportXlsxPaymentPlanButton';
import { DownloadPaymentPlanXlsxButton } from './actions/DownloadPaymentPlanXlsxButton';
import { SendXlsxPasswordPaymentPlanButton } from './actions/SendXlsxPasswordPaymentPlanButton';
import { DeliveryExportXlsxWithAuthCodePaymentPlanButton } from './actions/DeliveryExportXlsxWithAuthCodePaymentPlanButton';
import { DeliveryImportXlsxPaymentPlanButton } from './actions/DeliveryImportXlsxPaymentPlanButton';
import { PaymentPlanClosureActionButton } from './actions/PaymentPlanClosureActionButton';
import { LockUnlockPaymentPlanButton } from './actions/LockUnlockPaymentPlanButton';
import { SendForApprovalPaymentPlanButton } from './actions/SendForApprovalPaymentPlanButton';
import { SendToPaymentGatewayPaymentPlanButton } from './actions/SendToPaymentGatewayPaymentPlanButton';
import { SplitPaymentPlanButton } from './actions/SplitPaymentPlanButton';
import type { PaymentPlanDetail } from './types';
import { isPaymentPlanBackgroundActionBusy } from './utils';
import { responsiveValue } from 'src/responsive';
import { HeaderActions } from '@core/HeaderActions';

// For each approval stage: the action that moves the payment plan forward
// and the permission it needs; Reject in that stage needs the same permission.
const STAGE_ACTIONS: Partial<
  Record<
    PaymentPlanStatusEnum,
    { action: PaymentPlanAcceptanceAction; permission: string }
  >
> = {
  [PaymentPlanStatusEnum.IN_APPROVAL]: {
    action: 'approve',
    permission: PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
  },
  [PaymentPlanStatusEnum.IN_AUTHORIZATION]: {
    action: 'authorize',
    permission: PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
  },
  [PaymentPlanStatusEnum.IN_REVIEW]: {
    action: 'markAsReleased',
    permission: PERMISSIONS.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
  },
};

function ApprovalButtons({
  paymentPlan,
}: {
  paymentPlan: PaymentPlanDetail | null;
}): ReactElement | null {
  const permissions = usePermissions();
  if (!paymentPlan || !permissions) return null;

  if (paymentPlan.status === PaymentPlanStatusEnum.LOCKED) {
    return hasPermissions(PERMISSIONS.PM_SEND_FOR_APPROVAL, permissions) ? (
      <SendForApprovalPaymentPlanButton paymentPlan={paymentPlan} />
    ) : null;
  }
  const stage = STAGE_ACTIONS[paymentPlan.status];
  if (!stage || !hasPermissions(stage.permission, permissions)) return null;
  return (
    <>
      <AcceptanceActionPaymentPlanButton
        paymentPlan={paymentPlan}
        action="reject"
      />
      <AcceptanceActionPaymentPlanButton
        paymentPlan={paymentPlan}
        action={stage.action}
      />
    </>
  );
}

const ABORTABLE_STATUSES: PaymentPlanStatusEnum[] = [
  PaymentPlanStatusEnum.LOCKED,
  PaymentPlanStatusEnum.IN_APPROVAL,
  PaymentPlanStatusEnum.IN_AUTHORIZATION,
  PaymentPlanStatusEnum.IN_REVIEW,
];

function ClosureButtons({
  paymentPlan,
}: {
  paymentPlan: PaymentPlanDetail | null;
}): ReactElement | null {
  const permissions = usePermissions();
  if (!paymentPlan?.status || !permissions) return null;
  const can = (permission: string) => hasPermissions(permission, permissions);

  if (ABORTABLE_STATUSES.includes(paymentPlan.status)) {
    return can(PERMISSIONS.PM_ABORT) ? (
      <AbortPaymentPlanButton paymentPlan={paymentPlan} />
    ) : null;
  }
  switch (paymentPlan.status) {
    case PaymentPlanStatusEnum.ABORTED:
      return can(PERMISSIONS.PM_REACTIVATE_ABORT) &&
        !isPaymentPlanBackgroundActionBusy(paymentPlan) ? (
        <PaymentPlanClosureActionButton
          paymentPlan={paymentPlan}
          action="reactivate"
        />
      ) : null;
    case PaymentPlanStatusEnum.FINISHED:
      return can(PERMISSIONS.PM_MARK_READY_FOR_CLOSURE) ? (
        <PaymentPlanClosureActionButton
          paymentPlan={paymentPlan}
          action="readyForClosure"
        />
      ) : null;
    case PaymentPlanStatusEnum.READY_FOR_CLOSURE:
      return (
        <>
          {can(PERMISSIONS.PM_MARK_READY_FOR_CLOSURE) && (
            <PaymentPlanClosureActionButton
              paymentPlan={paymentPlan}
              action="sendBack"
            />
          )}
          {can(PERMISSIONS.PM_CLOSE_FINISHED) && (
            <ClosePaymentPlanButton paymentPlan={paymentPlan} />
          )}
        </>
      );
    default:
      return null;
  }
}

function LinkedPaymentPlanButtons({
  paymentPlan,
}: {
  paymentPlan: PaymentPlanDetail | null;
}): ReactElement | null {
  if (!paymentPlan) return null;
  return (
    <>
      {paymentPlan.canCreateFollowUp && (
        <CreateLinkedPaymentPlanButton
          paymentPlan={paymentPlan}
          variant="followup"
        />
      )}
      {paymentPlan.canCreateTopUp && (
        <CreateLinkedPaymentPlanButton
          paymentPlan={paymentPlan}
          variant="topup"
        />
      )}
      {paymentPlan.canCreateTopUpAmendment && (
        <CreateLinkedPaymentPlanButton
          paymentPlan={paymentPlan}
          variant="amendment"
        />
      )}
    </>
  );
}

interface PaymentPlanDetailsHeaderProps {
  paymentPlan: PaymentPlanDetail | null;
}

export function PaymentPlanDetailsHeader({
  paymentPlan,
}: PaymentPlanDetailsHeaderProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/program-cycles`,
    },
    {
      title: t('Payment Plans'),
      to: `/${baseUrl}/payment-module/payment-plans`,
    },
  ];

  return (
    <PageHeader
      title={
        <Box
          sx={{
            display: 'flex',
            flexWrap: responsiveValue('wrap', 'nowrap'),
            alignItems: 'baseline',
            gap: 1,
          }}
        >
          <Box>{paymentPlan?.name ?? t('Payment Plan')}</Box>
          {paymentPlan?.unicefId && (
            <Box
              sx={{
                color: 'text.secondary',
                fontSize: '0.85em',
              }}
            >
              {paymentPlan.unicefId}
            </Box>
          )}
          {paymentPlan?.status && (
            <Box>
              <StatusBox
                status={paymentPlan.status}
                statusToColor={paymentListStatusToColor}
                dataCy="group-status"
              />
            </Box>
          )}
          {paymentPlan?.backgroundActionStatus && (
            <Box>
              <StatusBox
                status={paymentPlan.backgroundActionStatus}
                statusToColor={paymentListBackgroundActionStatusToColor}
                dataCy="group-background-action-status"
              />
            </Box>
          )}
        </Box>
      }
      breadCrumbs={breadCrumbsItems}
      flags={<AdminButton adminUrl={paymentPlan?.adminUrl} />}
    >
      <HeaderActions spacing="none">
        <EditPaymentPlan paymentPlan={paymentPlan} />
        <LockUnlockPaymentPlanButton paymentPlan={paymentPlan} />
        <ApprovalButtons paymentPlan={paymentPlan} />
        <ClosureButtons paymentPlan={paymentPlan} />
        <DeliveryExportXlsxPaymentPlanButton paymentPlan={paymentPlan} />
        <DeliveryExportXlsxWithAuthCodePaymentPlanButton
          paymentPlan={paymentPlan}
        />
        <DownloadPaymentPlanXlsxButton paymentPlan={paymentPlan} />
        <SendXlsxPasswordPaymentPlanButton paymentPlan={paymentPlan} />
        <DeliveryImportXlsxPaymentPlanButton paymentPlan={paymentPlan} />
        <SplitPaymentPlanButton paymentPlan={paymentPlan} />
        <SendToPaymentGatewayPaymentPlanButton paymentPlan={paymentPlan} />
        <LinkedPaymentPlanButtons paymentPlan={paymentPlan} />
        <DeletePaymentPlan paymentPlan={paymentPlan} />
      </HeaderActions>
    </PageHeader>
  );
}
