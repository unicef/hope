import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box } from '@mui/material';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { DeletePaymentPlanGroup } from './actions/DeletePaymentPlanGroup';
import { EditGroupName } from './actions/EditGroupName';
import { ExportGroupButton } from './actions/ExportGroupButton';
import { SendToPaymentGatewayGroupButton } from './actions/SendToPaymentGatewayGroupButton';
import { PaymentPlanGroupDetail } from './types';

interface PaymentPlanGroupDetailHeaderProps {
  group: PaymentPlanGroupDetail | null;
}

export function PaymentPlanGroupDetailHeader({
  group,
}: PaymentPlanGroupDetailHeaderProps): ReactElement {
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
        <Box display="flex" alignItems="center" gap={1}>
          <Box>{group?.name ?? t('Group Detail')}</Box>
          {group?.unicefId && (
            <Box color="text.secondary" fontSize="0.85em">
              {group.unicefId}
            </Box>
          )}
        </Box>
      }
      breadCrumbs={breadCrumbsItems}
    >
      <Box display="flex" alignItems="center">
        <EditGroupName group={group} />
        <ExportGroupButton group={group} />
        <SendToPaymentGatewayGroupButton group={group} />
        <DeletePaymentPlanGroup group={group} />
      </Box>
    </PageHeader>
  );
}
