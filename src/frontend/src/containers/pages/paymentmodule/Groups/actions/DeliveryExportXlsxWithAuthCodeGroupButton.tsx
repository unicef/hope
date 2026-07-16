import { PaymentPlanGroupDeliveryExportPlanTypeEnum } from '@restgenerated/models/PaymentPlanGroupDeliveryExportPlanTypeEnum';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanGroupDetail } from '../types';
import { isGroupBackgroundActionBusy } from '../utils';
import {
  GroupExportPlanTypeOption,
  GroupExportXlsxDialog,
} from './GroupExportXlsxDialog';

interface DeliveryExportXlsxWithAuthCodeGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function DeliveryExportXlsxWithAuthCodeGroupButton({
  group,
}: DeliveryExportXlsxWithAuthCodeGroupButtonProps): ReactElement | null {
  const { t } = useTranslation();

  const planTypeOptions: GroupExportPlanTypeOption[] = [
    ...(group?.canExportRegular
      ? [
          {
            value: PaymentPlanGroupDeliveryExportPlanTypeEnum.REGULAR,
            label: t('Regular'),
          },
        ]
      : []),
    ...(group?.canExportFollowUp
      ? [
          {
            value: PaymentPlanGroupDeliveryExportPlanTypeEnum.FOLLOW_UP,
            label: t('Follow Up'),
          },
        ]
      : []),
    ...(group?.canExportTopUp
      ? [
          {
            value: PaymentPlanGroupDeliveryExportPlanTypeEnum.TOP_UP,
            label: t('Top Up'),
          },
        ]
      : []),
  ];

  if (group && planTypeOptions.length === 0) return null;

  return (
    <GroupExportXlsxDialog
      groupId={group?.id ?? ''}
      planTypeOptions={planTypeOptions}
      buttonLabel={t('Export with Auth Code')}
      dialogTitle={t('Export with Auth Code')}
      buttonVariant="outlined"
      disabled={!group || isGroupBackgroundActionBusy(group)}
      dataCySuffix="delivery-export-xlsx-with-auth-code-group"
    />
  );
}
