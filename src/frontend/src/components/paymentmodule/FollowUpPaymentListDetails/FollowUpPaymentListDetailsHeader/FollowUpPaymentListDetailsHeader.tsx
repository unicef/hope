import { Box } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import {
  paymentListBackgroundActionStatusToColor,
  paymentListStatusToColor,
} from '@utils/utils';
import type { BreadCrumbsItem } from '../../../core/BreadCrumbs';
import { PageHeader } from '../../../core/PageHeader';
import { StatusBox } from '../../../core/StatusBox';
import { LockedPaymentListHeaderButtons } from '../../PaymentListDetails/PaymentListDetailsHeader/HeaderButtons/LockedPaymentListHeaderButtons';
import { OpenPaymentListHeaderButtons } from '../../PaymentListDetails/PaymentListDetailsHeader/HeaderButtons/OpenPaymentListHeaderButtons';
import type { ReactElement } from 'react';
import type { PaymentListDetail } from '@restgenerated/models/PaymentListDetail';
import { AdminButton } from '@components/core/AdminButton';
import { responsiveValue } from 'src/responsive';

const StatusWrapper = styled.div`
  margin-left: 30px;
`;

interface FollowUpPaymentListDetailsHeaderProps {
  baseUrl: string;
  permissions: string[];
  paymentList: PaymentListDetail;
}

export function FollowUpPaymentListDetailsHeader({
  baseUrl,
  permissions,
  paymentList,
}: FollowUpPaymentListDetailsHeaderProps): ReactElement {
  const { isInstructionManaged } = paymentList;
  const { t } = useTranslation();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/payment-plans`,
    },
  ];
  if (paymentList.paymentPlan) {
    breadCrumbsItems.push({
      title: paymentList.paymentPlan.name,
      to: `/${baseUrl}/payment-module/payment-plans/${paymentList.paymentPlan.id}`,
    });
  }

  const canRemove =
    hasPermissions(PERMISSIONS.PM_CREATE, permissions) && paymentList.canDelete;
  const canLock = hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK, permissions);
  const canUnlock = hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK, permissions);

  let buttons: ReactElement | null = null;
  switch (paymentList.status) {
    case 'OPEN':
      buttons = isInstructionManaged ? null : (
        <OpenPaymentListHeaderButtons
          paymentList={paymentList}
          canRemove={canRemove}
          canLock={canLock}
        />
      );
      break;
    case 'LOCKED':
      buttons = isInstructionManaged ? null : (
        <LockedPaymentListHeaderButtons
          paymentList={paymentList}
          canUnlock={canUnlock}
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
            flexWrap: responsiveValue('wrap', 'nowrap'),
            rowGap: 2,
            alignItems: 'center',
          }}
        >
          {t('Follow-up Payment List')} ID:{' '}
          <Box
            sx={{
              ml: 1,
            }}
          >
            <span data-cy="pp-unicef-id">{paymentList.unicefId}</span>
          </Box>
          <StatusWrapper>
            <StatusBox
              status={paymentList.status}
              statusToColor={paymentListStatusToColor}
            />
          </StatusWrapper>
          {paymentList.backgroundActionStatus && (
            <StatusWrapper>
              <StatusBox
                status={paymentList.backgroundActionStatus}
                statusToColor={paymentListBackgroundActionStatusToColor}
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
      flags={<AdminButton adminUrl={paymentList.adminUrl} />}
    >
      {buttons}
    </PageHeader>
  );
}
