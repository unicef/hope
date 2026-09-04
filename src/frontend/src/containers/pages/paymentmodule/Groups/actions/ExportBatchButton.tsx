import { usePermissions } from '@hooks/usePermissions';
import type { PlanTypeEnum } from '@restgenerated/models/PlanTypeEnum';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { GroupExportXlsxDialog } from './GroupExportXlsxDialog';

interface ExportBatchButtonProps {
  groupId: string;
  tag: string;
  planType?: PlanTypeEnum;
  isBusy?: boolean;
}

export function ExportBatchButton({
  groupId,
  tag,
  planType,
  isBusy = false,
}: ExportBatchButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const permissions = usePermissions();

  if (
    !hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX, permissions)
  )
    return null;

  return (
    <GroupExportXlsxDialog
      groupId={groupId}
      exportTag={parseInt(tag, 10)}
      lockedPlanType={planType}
      buttonLabel={t('Re-export Batch')}
      dialogTitle={t('Re-export Batch #{{tag}}', { tag })}
      buttonVariant="contained"
      disabled={!groupId || !tag || isBusy}
      dataCySuffix="export-batch"
    />
  );
}
