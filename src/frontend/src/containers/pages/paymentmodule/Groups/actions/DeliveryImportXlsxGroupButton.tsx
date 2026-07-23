import { XlsxImportDialog } from '@core/XlsxImportDialog';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { PaymentPlanImportFile } from '@restgenerated/models/PaymentPlanImportFile';
import { RestService } from '@restgenerated/services/RestService';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { PaymentPlanGroupDetail } from '../types';
import { isGroupBackgroundActionBusy } from '../utils';

interface DeliveryImportXlsxGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function DeliveryImportXlsxGroupButton({
  group,
}: DeliveryImportXlsxGroupButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const permissions = usePermissions();

  if (
    !hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX, permissions)
  )
    return null;

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
