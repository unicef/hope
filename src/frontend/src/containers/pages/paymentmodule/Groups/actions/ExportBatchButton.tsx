import { PlanTypeEnum } from '@restgenerated/models/PlanTypeEnum';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
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
}: ExportBatchButtonProps): ReactElement {
  const { t } = useTranslation();
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
