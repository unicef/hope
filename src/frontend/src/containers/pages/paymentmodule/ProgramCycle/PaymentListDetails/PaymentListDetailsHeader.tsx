import { LockedPaymentListHeaderButtons } from '@components/paymentmodule/PaymentListDetails/PaymentListDetailsHeader/HeaderButtons/LockedPaymentListHeaderButtons';
import { OpenPaymentListHeaderButtons } from '@components/paymentmodule/PaymentListDetails/PaymentListDetailsHeader/HeaderButtons/OpenPaymentListHeaderButtons';
import { AdminButton } from '@core/AdminButton';
import type { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { StatusBox } from '@core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box } from '@mui/material';
import type { PaymentListDetail } from '@restgenerated/models/PaymentListDetail';
import {
  paymentListBackgroundActionStatusToColor,
  paymentListStatusToColor,
} from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { PaymentListStatusEnum } from '@restgenerated/models/PaymentListStatusEnum';
import { responsiveValue } from 'src/responsive';

interface PaymentListDetailsHeaderProps {
  permissions: string[];
  paymentList: PaymentListDetail;
}

export const PaymentListDetailsHeader = ({
  permissions,
  paymentList,
}: PaymentListDetailsHeaderProps): ReactElement => {
  const { isInstructionManaged } = paymentList;
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const programCycleId = paymentList.programCycle?.id;

  const breadCrumbsItems: BreadCrumbsItem[] = [];

  if (programCycleId) {
    breadCrumbsItems.push({
      title: t('Payment Module'),
      to: '../../..',
    });
    breadCrumbsItems.push({
      title: paymentList.programCycle?.title || '',
      to: '../..',
    });
  } else {
    breadCrumbsItems.push({
      title: t('Payment Module'),
      to: '..',
    });
  }

  if (paymentList.paymentPlan) {
    breadCrumbsItems.push({
      title: paymentList.paymentPlan.name,
      to: `/${baseUrl}/payment-module/payment-plans/${paymentList.paymentPlan.id}`,
    });
  }

  const canRemove =
    hasPermissions(PERMISSIONS.PM_CREATE, permissions) && paymentList.canDelete;
  const canLock = hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK, permissions);

  let buttons: ReactElement | null = null;
  switch (paymentList.status) {
    case PaymentListStatusEnum.OPEN:
      buttons = isInstructionManaged ? null : (
        <OpenPaymentListHeaderButtons
          paymentList={paymentList}
          canRemove={canRemove}
          canLock={canLock}
        />
      );
      break;
    case PaymentListStatusEnum.LOCKED:
      buttons = isInstructionManaged ? null : (
        <LockedPaymentListHeaderButtons
          paymentList={paymentList}
          canUnlock={canLock}
        />
      );
      break;
    case PaymentListStatusEnum.CLOSED:
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
            flexWrap: responsiveValue('wrap', 'nowrap'),
            rowGap: 2,
            alignItems: 'center',
          }}
        >
          {t('Payment List')} ID:{' '}
          <Box
            sx={{
              ml: 1,
              mr: 2,
            }}
          >
            <span data-cy="pp-unicef-id">{paymentList.unicefId}</span>
          </Box>
          <Box
            sx={{
              mr: 2,
            }}
          >
            <StatusBox
              status={paymentList.status}
              statusToColor={paymentListStatusToColor}
            />
          </Box>
          <Box
            sx={{
              mr: 2,
            }}
          >
            {paymentList.backgroundActionStatus && (
              <StatusBox
                status={paymentList.backgroundActionStatus}
                statusToColor={paymentListBackgroundActionStatusToColor}
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
      flags={<AdminButton adminUrl={paymentList.adminUrl} />}
    >
      {buttons}
    </PageHeader>
  );
};
