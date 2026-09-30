import { AdminButton } from '@core/AdminButton';
import type { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { StatusBox } from '@core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box } from '@mui/material';
import {
  paymentPlanBackgroundActionStatusToColor,
  paymentPlanStatusToColor,
} from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { DeletePaymentPlanGroup } from './actions/DeletePaymentPlanGroup';
import { EditGroup } from './actions/EditGroup';
import { DeliveryExportXlsxGroupButton } from './actions/DeliveryExportXlsxGroupButton';
import { DeliveryExportXlsxWithAuthCodeGroupButton } from './actions/DeliveryExportXlsxWithAuthCodeGroupButton';
import { DeliveryImportXlsxGroupButton } from './actions/DeliveryImportXlsxGroupButton';
import { LockUnlockGroupButton } from './actions/LockUnlockGroupButton';
import { SendToPaymentGatewayGroupButton } from './actions/SendToPaymentGatewayGroupButton';
import type { PaymentPlanGroupDetail } from './types';

interface PaymentPlanGroupDetailsHeaderProps {
  group: PaymentPlanGroupDetail | null;
}

export function PaymentPlanGroupDetailsHeader({
  group,
}: PaymentPlanGroupDetailsHeaderProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/program-cycles`,
    },
    {
      title: t('Groups'),
      to: `/${baseUrl}/payment-module/groups`,
    },
  ];

  return (
    <PageHeader
      title={
        <Box
          sx={{
            display: 'flex',
            alignItems: 'baseline',
            gap: 1,
          }}
        >
          <Box>{group?.name ?? t('Group Detail')}</Box>
          {group?.unicefId && (
            <Box
              sx={{
                color: 'text.secondary',
                fontSize: '0.85em',
              }}
            >
              {group.unicefId}
            </Box>
          )}
          {group?.status && (
            <Box>
              <StatusBox
                status={group.status}
                statusToColor={paymentPlanStatusToColor}
                dataCy="group-status"
              />
            </Box>
          )}
          {group?.backgroundActionStatus && (
            <Box>
              <StatusBox
                status={group.backgroundActionStatus}
                statusToColor={paymentPlanBackgroundActionStatusToColor}
                dataCy="group-background-action-status"
              />
            </Box>
          )}
        </Box>
      }
      breadCrumbs={breadCrumbsItems}
      flags={<AdminButton adminUrl={group?.adminUrl} />}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <EditGroup group={group} />
        <LockUnlockGroupButton group={group} />
        <DeliveryExportXlsxGroupButton group={group} />
        <DeliveryExportXlsxWithAuthCodeGroupButton group={group} />
        <DeliveryImportXlsxGroupButton group={group} />
        <SendToPaymentGatewayGroupButton group={group} />
        <DeletePaymentPlanGroup group={group} />
      </Box>
    </PageHeader>
  );
}
