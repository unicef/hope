import { Box } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import {
  paymentPlanBackgroundActionStatusToColor,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { PageHeader } from '../../../core/PageHeader';
import { StatusBox } from '../../../core/StatusBox';
import { AcceptedPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/AcceptedPaymentPlanHeaderButtons';
import { FinishedPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/FinishedPaymentPlanHeaderButtons';
import { ReadyForClosurePaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/ReadyForClosurePaymentPlanHeaderButtons';
import { InApprovalPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/InApprovalPaymentPlanHeaderButtons';
import { InAuthorizationPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/InAuthorizationPaymentPlanHeaderButtons';
import { InReviewPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/InReviewPaymentPlanHeaderButtons';
import { LockedFspPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/LockedFspPaymentPlanHeaderButtons';
import { LockedPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/LockedPaymentPlanHeaderButtons';
import { OpenPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/OpenPaymentPlanHeaderButtons';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { AdminButton } from '@components/core/AdminButton';

const StatusWrapper = styled.div`
  margin-left: 30px;
`;

interface FollowUpPaymentPlanDetailsHeaderProps {
  baseUrl: string;
  permissions: string[];
  paymentPlan: PaymentPlanDetail;
}

export function FollowUpPaymentPlanDetailsHeader({
  baseUrl,
  permissions,
  paymentPlan,
}: FollowUpPaymentPlanDetailsHeaderProps): ReactElement {
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

  const canClose = hasPermissions(PERMISSIONS.PM_CLOSE_FINISHED, permissions);
  const canMarkReadyForClosure = hasPermissions(
    PERMISSIONS.PM_MARK_READY_FOR_CLOSURE,
    permissions,
  );

  const canSplit =
    hasPermissions(PERMISSIONS.PM_SPLIT, permissions) && paymentPlan.canSplit;
  const canSendToPaymentGateway =
    hasPermissions(PERMISSIONS.PM_SEND_TO_PAYMENT_GATEWAY, permissions) &&
    paymentPlan.canSendToPaymentGateway;
  const canAbort = hasPermissions(PERMISSIONS.PM_ABORT, permissions);

  const { isInstructionManaged } = paymentPlan;

  let buttons: ReactElement | null = null;
  switch (paymentPlan.status) {
    case 'OPEN':
      buttons = isInstructionManaged ? null : (
        <OpenPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canRemove={canRemove}
          canEdit={canEdit}
          canLock={canLock}
        />
      );
      break;
    case 'LOCKED':
      buttons = isInstructionManaged ? null : (
        <LockedPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canUnlock={canUnlock}
          permissions={permissions}
          canAbort={canAbort}
        />
      );
      break;
    case 'LOCKED_FSP':
      buttons = isInstructionManaged ? null : (
        <LockedFspPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canUnlock={canUnlock}
          canSendForApproval={canSendForApproval}
          canAbort={canAbort}
        />
      );
      break;
    case 'IN_APPROVAL':
      buttons = isInstructionManaged ? null : (
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
    case 'IN_AUTHORIZATION':
      buttons = isInstructionManaged ? null : (
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
    case 'IN_REVIEW':
      buttons = isInstructionManaged ? null : (
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
    case 'ACCEPTED':
      buttons = (
        <AcceptedPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canSplit={canSplit}
        />
      );
      break;
    case 'FINISHED':
      buttons = (
        <FinishedPaymentPlanHeaderButtons
          canSendToPaymentGateway={canSendToPaymentGateway}
          paymentPlan={paymentPlan}
          canSplit={canSplit}
          canMarkReadyForClosure={canMarkReadyForClosure}
        />
      );
      break;
    case 'READY_FOR_CLOSURE':
      buttons = (
        <ReadyForClosurePaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canSendBack={canMarkReadyForClosure}
          canClose={canClose}
        />
      );
      break;
    case 'CLOSED':
      buttons = null;
      break;
    default:
      break;
  }

  return (
    <PageHeader
      title={
        <Box display="flex" alignItems="center">
          {t('Follow-up Payment Plan')} ID:{' '}
          <Box ml={1}>
            <span data-cy="pp-unicef-id">{paymentPlan.unicefId}</span>
          </Box>
          <StatusWrapper>
            <StatusBox
              status={paymentPlan.status}
              statusToColor={paymentPlanStatusToColor}
            />
          </StatusWrapper>
          {paymentPlan.backgroundActionStatus && (
            <StatusWrapper>
              <StatusBox
                status={paymentPlan.backgroundActionStatus}
                statusToColor={paymentPlanBackgroundActionStatusToColor}
              />
            </StatusWrapper>
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
