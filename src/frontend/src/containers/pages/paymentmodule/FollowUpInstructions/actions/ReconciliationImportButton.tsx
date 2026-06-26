import { XlsxImportDialog } from '@core/XlsxImportDialog';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import { PaymentPlanImportFile } from '@restgenerated/models/PaymentPlanImportFile';
import { RestService } from '@restgenerated/services/RestService';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

interface ReconciliationImportButtonProps {
  instruction: FollowUpInstructionDetail;
}

export function ReconciliationImportButton({
  instruction,
}: ReconciliationImportButtonProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();

  return (
    <XlsxImportDialog
      mutationFn={(formData: PaymentPlanImportFile) =>
        RestService.restBusinessAreasProgramsFollowUpInstructionsDeliveryImportXlsxCreate(
          {
            businessAreaSlug: businessArea,
            id: instruction.id,
            programCode: programId,
            formData,
          },
        )
      }
      invalidateQueryKey={[
        'followUpInstruction',
        businessArea,
        instruction.id,
        programId,
      ]}
      successMessage={t('Reconciliation import started')}
      buttonLabel={t('Upload Reconciliation')}
      dataCySuffix="reconciliation-import"
    />
  );
}
