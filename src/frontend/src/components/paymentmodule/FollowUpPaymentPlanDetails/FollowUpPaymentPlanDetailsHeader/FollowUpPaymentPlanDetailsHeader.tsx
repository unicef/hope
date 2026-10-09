import { Box } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import {
  paymentPlanBackgroundActionStatusToColor,
  paymentPlanStatusToColor,
} from '@utils/utils';
import type { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { PageHeader } from '../../../core/PageHeader';
import { StatusBox } from '../../../core/StatusBox';
import { AcceptedPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/AcceptedPaymentPlanHeaderButtons';
import { FinishedPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/FinishedPaymentPlanHeaderButtons';
import { LockedPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/LockedPaymentPlanHeaderButtons';
import { OpenPaymentPlanHeaderButtons } from '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/OpenPaymentPlanHeaderButtons';
import type { ReactElement } from 'react';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
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
  const visionManaged = paymentPlan.visionManaged;
  const { t } = useTranslation();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/payment-plans`,
    },
  ];

  const canRemove =
    hasPermissions(PERMISSIONS.PM_CREATE, permissions) && paymentPlan.canDelete;
  const canEdit = hasPermissions(PERMISSIONS.PM_CREATE, permissions);
  const canLock = hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK, permissions);
  const canUnlock = hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK, permissions);

  const canSendToPaymentGateway =
    hasPermissions(PERMISSIONS.PM_SEND_TO_PAYMENT_GATEWAY, permissions) &&
    paymentPlan.canSendToPaymentGateway &&
    !visionManaged;

  const canSplit =
    hasPermissions(PERMISSIONS.PM_SPLIT, permissions) && paymentPlan.canSplit;

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
          canUnlock={canUnlock}
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
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
          }}
        >
          {t('Follow-up Payment Plan')} ID:{' '}
          <Box
            sx={{
              ml: 1,
            }}
          >
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
