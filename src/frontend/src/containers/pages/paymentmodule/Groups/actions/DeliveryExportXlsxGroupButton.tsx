import { usePermissions } from '@hooks/usePermissions';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
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
  const permissions = usePermissions();

  if (
    !hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX, permissions)
  )
    return null;
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
