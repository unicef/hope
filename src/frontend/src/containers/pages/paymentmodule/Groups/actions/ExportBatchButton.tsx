import { usePermissions } from '@hooks/usePermissions';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { GroupExportXlsxDialog } from './GroupExportXlsxDialog';

interface ExportBatchButtonProps {
  groupId: string;
  tag: string;
  isBusy?: boolean;
}

export function ExportBatchButton({
  groupId,
  tag,
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
      buttonLabel={t('Re-export Batch')}
      dialogTitle={t('Re-export Batch #{{tag}}', { tag })}
      buttonVariant="contained"
      disabled={!groupId || !tag || isBusy}
      dataCySuffix="export-batch"
    />
  );
}
