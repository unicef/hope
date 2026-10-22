import { usePermissions } from '@hooks/usePermissions';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import type { PaymentPlanGroupDetail } from '../types';
import { isGroupBackgroundActionBusy } from '../utils';
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
  if (group && !group.canExport && !group.canRegenerateExport) return null;
  const label = group?.canRegenerateExport ? t('Re-export') : t('Export');

  return (
    <GroupExportXlsxDialog
      groupId={group?.id ?? ''}
      showTemplateChoice={false}
      buttonLabel={label}
      dialogTitle={label}
      buttonVariant="contained"
      disabled={!group || isGroupBackgroundActionBusy(group)}
      dataCySuffix="delivery-export-xlsx-group"
    />
  );
}
