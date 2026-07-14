import { XlsxImportDialog } from '@core/XlsxImportDialog';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaymentPlanImportFile } from '@restgenerated/models/PaymentPlanImportFile';
import { RestService } from '@restgenerated/services/RestService';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanGroupDetail } from '../types';
import { isGroupBackgroundActionBusy } from '../utils';

interface DeliveryImportXlsxGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function DeliveryImportXlsxGroupButton({
  group,
}: DeliveryImportXlsxGroupButtonProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();

  return (
    <XlsxImportDialog
      mutationFn={(formData: PaymentPlanImportFile) =>
        RestService.restBusinessAreasProgramsPaymentPlanGroupsDeliveryImportXlsxCreate(
          {
            businessAreaSlug: businessArea,
            id: group?.id,
            programCode: programId,
            formData,
          },
        )
      }
      invalidateQueryKey={[
        'paymentPlanGroup',
        businessArea,
        programId,
        group?.id,
      ]}
      successMessage={t('Delivery reconciliation import started')}
      errorFallback={t('Import failed')}
      buttonLabel={t('Upload Reconciliation')}
      buttonVariant="contained"
      buttonMargin={2}
      disabled={!group || isGroupBackgroundActionBusy(group)}
      dataCySuffix="delivery-import-xlsx-group"
    />
  );
}
