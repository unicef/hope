import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanGroupDetail } from '../types';
import {
  exportablePlanTypeOptions,
  isGroupBackgroundActionBusy,
} from '../utils';
import { GroupExportXlsxDialog } from './GroupExportXlsxDialog';

interface DeliveryExportXlsxGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function DeliveryExportXlsxGroupButton({
  group,
}: DeliveryExportXlsxGroupButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const planTypeOptions = exportablePlanTypeOptions(group, t);

  if (group && planTypeOptions.length === 0) return null;

  return (
    <GroupExportXlsxDialog
      groupId={group?.id ?? ''}
      planTypeOptions={planTypeOptions}
      showTemplateChoice={false}
      buttonLabel={t('Export')}
      dialogTitle={t('Export')}
      buttonVariant="contained"
      disabled={!group || isGroupBackgroundActionBusy(group)}
      dataCySuffix="delivery-export-xlsx-group"
    />
  );
}
