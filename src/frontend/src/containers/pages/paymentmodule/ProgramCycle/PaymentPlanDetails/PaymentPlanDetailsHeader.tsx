import { Box } from '@mui/material';
import { PaymentPlanQuery } from '@generated/graphql';
import { useTranslation } from 'react-i18next';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { ReactElement } from 'react';
import { OpenPaymentPlanHeaderButtons } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/OpenPaymentPlanHeaderButtons';
import { LockedPaymentPlanHeaderButtons } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/LockedPaymentPlanHeaderButtons';
import { LockedFspPaymentPlanHeaderButtons } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/LockedFspPaymentPlanHeaderButtons';
import { InApprovalPaymentPlanHeaderButtons } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/InApprovalPaymentPlanHeaderButtons';
import { InAuthorizationPaymentPlanHeaderButtons } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/InAuthorizationPaymentPlanHeaderButtons';
import { InReviewPaymentPlanHeaderButtons } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/InReviewPaymentPlanHeaderButtons';
import { AcceptedPaymentPlanHeaderButtons } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/AcceptedPaymentPlanHeaderButtons';
import { PageHeader } from '@core/PageHeader';
import { StatusBox } from '@core/StatusBox';
import {
  decodeIdString,
  paymentPlanBackgroundActionStatusToColor,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { useQuery } from '@tanstack/react-query';
import { fetchProgramCycle } from '@api/programCycleApi';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { AdminButton } from '@core/AdminButton';

interface PaymentPlanDetailsHeaderProps {
  permissions: string[];
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const PaymentPlanDetailsHeader = ({
  permissions,
  paymentPlan,
}: PaymentPlanDetailsHeaderProps): ReactElement => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const programCycleId = paymentPlan.programCycle?.id;
  const { data: programCycleData } = useQuery({
    queryKey: [
      'programCyclesDetails',
      businessArea,
      programId,
      decodeIdString(programCycleId),
    ],
    queryFn: async () => {
      return fetchProgramCycle(
        businessArea,
        programId,
        decodeIdString(programCycleId),
      );
    },
    enabled: !!programCycleId,
  });

  const breadCrumbsItems: BreadCrumbsItem[] = [];

  if (programCycleId) {
    breadCrumbsItems.push({
      title: t('Payment Module'),
      to: '../../..',
    });
    breadCrumbsItems.push({
      title: `${programCycleData?.title || ''}`,
      to: '../..',
    });
  } else {
    breadCrumbsItems.push({
      title: t('Payment Module'),
      to: '..',
    });
  }

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
  const canSplit =
    hasPermissions(PERMISSIONS.PM_SPLIT, permissions) && paymentPlan.canSplit;
  const canSendToPaymentGateway =
    hasPermissions(PERMISSIONS.PM_SEND_TO_PAYMENT_GATEWAY, permissions) &&
    paymentPlan.canSendToPaymentGateway;

  let buttons: ReactElement | null = null;
  switch (paymentPlan.status) {
    case 'OPEN':
      buttons = (
        <OpenPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canRemove={canRemove}
          canEdit={canEdit}
          canLock={canLock}
        />
      );
      break;
    case 'LOCKED':
      buttons = (
        <LockedPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canUnlock={canLock}
          permissions={permissions}
        />
      );
      break;
    case 'LOCKED_FSP':
      buttons = (
        <LockedFspPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canUnlock={canUnlock}
          canSendForApproval={canSendForApproval}
        />
      );
      break;
    case 'IN_APPROVAL':
      buttons = (
        <InApprovalPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canReject={hasPermissions(
            PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
            permissions,
          )}
          canApprove={canApprove}
        />
      );
      break;
    case 'IN_AUTHORIZATION':
      buttons = (
        <InAuthorizationPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canReject={hasPermissions(
            PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
            permissions,
          )}
          canAuthorize={canAuthorize}
        />
      );
      break;
    case 'IN_REVIEW':
      buttons = (
        <InReviewPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canReject={hasPermissions(
            PERMISSIONS.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
            permissions,
          )}
          canMarkAsReleased={canMarkAsReleased}
        />
      );
      break;
    case 'FINISHED':
    case 'ACCEPTED':
      buttons = (
        <AcceptedPaymentPlanHeaderButtons
          canSendToPaymentGateway={canSendToPaymentGateway}
          canSplit={canSplit}
          paymentPlan={paymentPlan}
        />
      );
      break;
    default:
      break;
  }

  return (
    <PageHeader
      title={
        <Box display="flex" alignItems="center">
          {t('Payment Plan')} ID:{' '}
          <Box ml={1} mr={2}>
            <span data-cy="pp-unicef-id">{paymentPlan.unicefId}</span>
          </Box>
          <Box mr={2}>
            <StatusBox
              status={paymentPlan.status}
              statusToColor={paymentPlanStatusToColor}
            />
          </Box>
          <Box mr={2}>
            {paymentPlan.backgroundActionStatus && (
              <StatusBox
                status={paymentPlan.backgroundActionStatus}
                statusToColor={paymentPlanBackgroundActionStatusToColor}
              />
            )}
          </Box>
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
};
