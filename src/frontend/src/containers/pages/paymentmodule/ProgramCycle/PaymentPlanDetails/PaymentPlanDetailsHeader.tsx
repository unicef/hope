import { LockedPaymentPlanHeaderButtons } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/LockedPaymentPlanHeaderButtons';
import { OpenPaymentPlanHeaderButtons } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/OpenPaymentPlanHeaderButtons';
import { AdminButton } from '@core/AdminButton';
import type { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { StatusBox } from '@core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box } from '@mui/material';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import {
  paymentPlanBackgroundActionStatusToColor,
  paymentPlanStatusToColor,
} from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';

interface PaymentPlanDetailsHeaderProps {
  permissions: string[];
  paymentPlan: PaymentPlanDetail;
}

export const PaymentPlanDetailsHeader = ({
  permissions,
  paymentPlan,
}: PaymentPlanDetailsHeaderProps): ReactElement => {
  const { isInstructionManaged } = paymentPlan;
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const programCycleId = paymentPlan.programCycle?.id;

  const breadCrumbsItems: BreadCrumbsItem[] = [];

  if (programCycleId) {
    breadCrumbsItems.push({
      title: t('Payment Module'),
      to: '../../..',
    });
    breadCrumbsItems.push({
      title: paymentPlan.programCycle?.title || '',
      to: '../..',
    });
  } else {
    breadCrumbsItems.push({
      title: t('Payment Module'),
      to: '..',
    });
  }

  if (paymentPlan.paymentPlanGroup) {
    breadCrumbsItems.push({
      title: paymentPlan.paymentPlanGroup.name,
      to: `/${baseUrl}/payment-module/groups/${paymentPlan.paymentPlanGroup.id}`,
    });
  }

  const canRemove =
    hasPermissions(PERMISSIONS.PM_CREATE, permissions) && paymentPlan.canDelete;
  const canLock = hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK, permissions);

  let buttons: ReactElement | null = null;
  switch (paymentPlan.status) {
    case PaymentPlanStatusEnum.OPEN:
      buttons = isInstructionManaged ? null : (
        <OpenPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canRemove={canRemove}
          canLock={canLock}
        />
      );
      break;
    case PaymentPlanStatusEnum.LOCKED:
      buttons = isInstructionManaged ? null : (
        <LockedPaymentPlanHeaderButtons
          paymentPlan={paymentPlan}
          canUnlock={canLock}
        />
      );
      break;
    case PaymentPlanStatusEnum.CLOSED:
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
          {t('Payment Plan Component')} ID:{' '}
          <Box
            sx={{
              ml: 1,
              mr: 2,
            }}
          >
            <span data-cy="pp-unicef-id">{paymentPlan.unicefId}</span>
          </Box>
          <Box
            sx={{
              mr: 2,
            }}
          >
            <StatusBox
              status={paymentPlan.status}
              statusToColor={paymentPlanStatusToColor}
            />
          </Box>
          <Box
            sx={{
              mr: 2,
            }}
          >
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
