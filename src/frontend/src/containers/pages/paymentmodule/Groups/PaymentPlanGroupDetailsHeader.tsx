import { AdminButton } from '@core/AdminButton';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box } from '@mui/material';
import { PaymentPlanGroupDeliveryExportPlanTypeEnum } from '@restgenerated/models/PaymentPlanGroupDeliveryExportPlanTypeEnum';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { DeletePaymentPlanGroup } from './actions/DeletePaymentPlanGroup';
import { EditGroupName } from './actions/EditGroupName';
import { DeliveryExportXlsxGroupButton } from './actions/DeliveryExportXlsxGroupButton';
import { DeliveryExportXlsxWithAuthCodeGroupButton } from './actions/DeliveryExportXlsxWithAuthCodeGroupButton';
import { DeliveryImportXlsxGroupButton } from './actions/DeliveryImportXlsxGroupButton';
import { SendToPaymentGatewayGroupButton } from './actions/SendToPaymentGatewayGroupButton';
import { PaymentPlanGroupDetail } from './types';

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
        <Box display="flex" alignItems="baseline" gap={1}>
          <Box>{group?.name ?? t('Group Detail')}</Box>
          {group?.unicefId && (
            <Box color="text.secondary" fontSize="0.85em">
              {group.unicefId}
            </Box>
          )}
        </Box>
      }
      breadCrumbs={breadCrumbsItems}
      flags={<AdminButton adminUrl={group?.adminUrl} />}
    >
      <Box display="flex" alignItems="center">
        <EditGroupName group={group} />
        {group?.canExportRegular && <DeliveryExportXlsxGroupButton group={group} />}
        {group?.canExportFollowUp && (
          <DeliveryExportXlsxGroupButton
            group={group}
            planType={PaymentPlanGroupDeliveryExportPlanTypeEnum.FOLLOW_UP}
            label={t('Export Follow Ups')}
          />
        )}
        {group?.canExportTopUp && (
          <DeliveryExportXlsxGroupButton
            group={group}
            planType={PaymentPlanGroupDeliveryExportPlanTypeEnum.TOP_UP}
            label={t('Export Top Ups')}
          />
        )}
        <DeliveryExportXlsxWithAuthCodeGroupButton group={group} />
        <DeliveryImportXlsxGroupButton group={group} />
        <SendToPaymentGatewayGroupButton group={group} />
        <DeletePaymentPlanGroup group={group} />
      </Box>
    </PageHeader>
  );
}
