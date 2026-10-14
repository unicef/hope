import { usePermissions } from '@hooks/usePermissions';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import type { PaymentPlanGroupDetail } from '../types';
import { isGroupBackgroundActionBusy } from '../utils';
import { GroupExportXlsxDialog } from './GroupExportXlsxDialog';

interface DeliveryExportXlsxWithAuthCodeGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function DeliveryExportXlsxWithAuthCodeGroupButton({
  group,
}: DeliveryExportXlsxWithAuthCodeGroupButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const permissions = usePermissions();

  if (
    !hasPermissions(
      PERMISSIONS.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX,
      permissions,
    ) ||
    !hasPermissions(PERMISSIONS.PM_DOWNLOAD_FSP_AUTH_CODE, permissions)
  )
    return null;
  if (group && !group.canExport && !group.canRegenerateExport) return null;
  const label = group?.canRegenerateExport ? t('Re-export') : t('Export');

  return (
    <GroupExportXlsxDialog
      groupId={group?.id ?? ''}
      buttonLabel={`${label} ${t('with Auth Code')}`}
      dialogTitle={`${label} ${t('with Auth Code')}`}
      buttonVariant="outlined"
      disabled={!group || isGroupBackgroundActionBusy(group)}
      dataCySuffix="delivery-export-xlsx-with-auth-code-group"
    />
  );
}
