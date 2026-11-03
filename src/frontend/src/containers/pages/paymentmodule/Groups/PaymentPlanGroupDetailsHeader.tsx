import { AdminButton } from '@core/AdminButton';
import type { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { StatusBox } from '@core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box } from '@mui/material';
import { paymentPlanBackgroundActionStatusToColor } from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { DeletePaymentPlanGroup } from './actions/DeletePaymentPlanGroup';
import { EditGroupName } from './actions/EditGroupName';
import { DeliveryExportXlsxGroupButton } from './actions/DeliveryExportXlsxGroupButton';
import { DeliveryExportXlsxWithAuthCodeGroupButton } from './actions/DeliveryExportXlsxWithAuthCodeGroupButton';
import { DeliveryImportXlsxGroupButton } from './actions/DeliveryImportXlsxGroupButton';
import { SendToPaymentGatewayGroupButton } from './actions/SendToPaymentGatewayGroupButton';
import type { PaymentPlanGroupDetail } from './types';
import { responsiveValue } from 'src/responsive';
import { HeaderActions } from '@core/HeaderActions';

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
            flexWrap: responsiveValue('wrap', 'nowrap'),
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
      <HeaderActions spacing="none">
        <EditGroupName group={group} />
        <DeliveryExportXlsxGroupButton group={group} />
        <DeliveryExportXlsxWithAuthCodeGroupButton group={group} />
        <DeliveryImportXlsxGroupButton group={group} />
        <SendToPaymentGatewayGroupButton group={group} />
        <DeletePaymentPlanGroup group={group} />
      </HeaderActions>
    </PageHeader>
  );
}
