import { PaymentPlanGroupDeliveryExportPlanTypeEnum } from '@restgenerated/models/PaymentPlanGroupDeliveryExportPlanTypeEnum';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanGroupDetail } from '../types';
import { isGroupBackgroundActionBusy, planTypeDisplayLabel } from '../utils';
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

  const toOption = (
    value: PaymentPlanGroupDeliveryExportPlanTypeEnum,
  ): GroupExportPlanTypeOption => ({
    value,
    label: t(planTypeDisplayLabel(value)),
  });
  const planTypeOptions: GroupExportPlanTypeOption[] = [
    ...(group?.canExportRegular
      ? [toOption(PaymentPlanGroupDeliveryExportPlanTypeEnum.REGULAR)]
      : []),
    ...(group?.canExportFollowUp
      ? [toOption(PaymentPlanGroupDeliveryExportPlanTypeEnum.FOLLOW_UP)]
      : []),
    ...(group?.canExportTopUp
      ? [toOption(PaymentPlanGroupDeliveryExportPlanTypeEnum.TOP_UP)]
      : []),
    ...(group?.canExportTopUpAmendment
      ? [toOption(PaymentPlanGroupDeliveryExportPlanTypeEnum.TOP_UP_AMENDMENT)]
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
