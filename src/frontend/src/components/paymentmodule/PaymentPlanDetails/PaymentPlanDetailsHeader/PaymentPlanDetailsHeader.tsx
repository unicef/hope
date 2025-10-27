import { Box } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import {
  paymentPlanBackgroundActionStatusToColor,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { StatusBox } from '@core/StatusBox';
import { AcceptedPaymentPlanHeaderButtons } from './HeaderButtons/AcceptedPaymentPlanHeaderButtons';
import { InApprovalPaymentPlanHeaderButtons } from './HeaderButtons/InApprovalPaymentPlanHeaderButtons';
import { InAuthorizationPaymentPlanHeaderButtons } from './HeaderButtons/InAuthorizationPaymentPlanHeaderButtons';
import { InReviewPaymentPlanHeaderButtons } from './HeaderButtons/InReviewPaymentPlanHeaderButtons';
import { LockedFspPaymentPlanHeaderButtons } from './HeaderButtons/LockedFspPaymentPlanHeaderButtons';
import { LockedPaymentPlanHeaderButtons } from './HeaderButtons/LockedPaymentPlanHeaderButtons';
import { OpenPaymentPlanHeaderButtons } from './HeaderButtons/OpenPaymentPlanHeaderButtons';
import { AdminButton } from '@core/AdminButton';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { AbortedPaymentPlanHeaderButtons } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/AbortedPaymentPlanHeaderButtons';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';

interface PaymentPlanDetailsHeaderProps {
  baseUrl: string;
  permissions: string[];
  paymentPlan: PaymentPlanDetail;
}

export function PaymentPlanDetailsHeader({
  baseUrl,
  permissions,
  paymentPlan,
}: PaymentPlanDetailsHeaderProps): ReactElement {
  const { t } = useTranslation();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/payment-plans`,
    },
  ];

  const canRemove = hasPermissions(PERMISSIONS.PM_CREATE, permissions);
  const canEdit = hasPermissions(PERMISSIONS.PM_CREATE, permissions);
  const canLock = hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK, permissions);
  const canUnlock = hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK, permissions);
  const canSendForApproval = hasPermissions(
    PERMISSIONS.PM_SEND_FOR_APPROVAL,
    permissions,
  );
  const canApprove = hasPermissions(
    PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
    permissions,
  );
  const canAuthorize = hasPermissions(
    PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
    permissions,
  );
  const canMarkAsReleased = hasPermissions(
    PERMISSIONS.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
    permissions,
  );
  const canSendToPaymentGateway =
    hasPermissions(PERMISSIONS.PM_SEND_TO_PAYMENT_GATEWAY, permissions) &&
    paymentPlan.canSendToPaymentGateway;
  const canSplit =
    hasPermissions(PERMISSIONS.PM_SPLIT, permissions) && paymentPlan.canSplit;

  const canClose = hasPermissions(PERMISSIONS.PM_CLOSE_FINISHED, permissions);
  const canAbort = hasPermissions(PERMISSIONS.PM_ABORT, permissions);
  const canReactivateAbort = hasPermissions(
    PERMISSIONS.PM_REACTIVATE_ABORT,
    permissions,
  );

  let buttons: ReactElement | null = null;
  switch (paymentPlan.status) {
    case PaymentPlanStatusEnum.OPEN:
      buttons = (
        <OpenPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canRemove={canRemove}
          canEdit={canEdit}
          canLock={canLock}
          canAbort={canAbort}
        />
      );
      break;
    case PaymentPlanStatusEnum.LOCKED:
      buttons = (
        <LockedPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canUnlock={canLock}
          permissions={permissions}
          canAbort={canAbort}
        />
      );
      break;
    case PaymentPlanStatusEnum.LOCKED_FSP:
      buttons = (
        <LockedFspPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canUnlock={canUnlock}
          canSendForApproval={canSendForApproval}
          canAbort={canAbort}
        />
      );
      break;
    case PaymentPlanStatusEnum.IN_APPROVAL:
      buttons = (
        <InApprovalPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canReject={hasPermissions(
            PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
            permissions,
          )}
          canApprove={canApprove}
          canAbort={canAbort}
        />
      );
      break;
    case PaymentPlanStatusEnum.IN_AUTHORIZATION:
      buttons = (
        <InAuthorizationPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canReject={hasPermissions(
            PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
            permissions,
          )}
          canAuthorize={canAuthorize}
          canAbort={canAbort}
        />
      );
      break;
    case PaymentPlanStatusEnum.IN_REVIEW:
      buttons = (
        <InReviewPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canReject={hasPermissions(
            PERMISSIONS.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
            permissions,
          )}
          canMarkAsReleased={canMarkAsReleased}
          canAbort={canAbort}
        />
      );
      break;
    case PaymentPlanStatusEnum.FINISHED:
    case PaymentPlanStatusEnum.ACCEPTED:
      buttons = (
        <AcceptedPaymentPlanHeaderButtons
          canSendToPaymentGateway={canSendToPaymentGateway}
          canSplit={canSplit}
          paymentPlan={paymentPlan}
          canClose={canClose}
          canAbort={canAbort}
        />
      );
      break;
    case PaymentPlanStatusEnum.ABORTED:
      buttons = (
        <AbortedPaymentPlanHeaderButtons canReactivate={canReactivate} />
      );
      break;
    default:
      break;
  }

  return (
    <PageHeader
      title={
        <Box display="flex" alignItems="center">
          <Box display="flex" flexDirection="column">
            <Box> {t('Payment Plan')} ID: </Box>
            <Box>
              <span data-cy="pp-unicef-id">{paymentPlan.unicefId}</span>
            </Box>
          </Box>
          <Box ml={2}>
            <StatusBox
              status={paymentPlan.status}
              statusToColor={paymentPlanStatusToColor}
            />
          </Box>
          {paymentPlan.backgroundActionStatus && (
            <Box>
              <StatusBox
                status={paymentPlan.backgroundActionStatus}
                statusToColor={paymentPlanBackgroundActionStatusToColor}
              />
            </Box>
          )}
        </Box>
      }
      breadCrumbs={
        hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions)
          ? breadCrumbsItems
          : null
      }
      flags={<AdminButton adminUrl={paymentPlan.adminUrl} />}
    >
      {buttons}
    </PageHeader>
  );
}
