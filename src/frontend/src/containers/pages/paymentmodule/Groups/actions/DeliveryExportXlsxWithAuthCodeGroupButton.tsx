import { usePermissions } from '@hooks/usePermissions';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import type { PaymentPlanGroupDetail } from '../types';
import {
  exportablePlanTypeOptions,
  isGroupBackgroundActionBusy,
} from '../utils';
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
  const planTypeOptions = exportablePlanTypeOptions(group, t);

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
