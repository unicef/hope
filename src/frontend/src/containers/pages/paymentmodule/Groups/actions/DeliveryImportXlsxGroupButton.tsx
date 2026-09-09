import { XlsxImportDialog } from '@core/XlsxImportDialog';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import {
  Checkbox,
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  Select,
} from '@mui/material';
import type { PaymentPlanImportFile } from '@restgenerated/models/PaymentPlanImportFile';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import type { PaymentPlanGroupDetail } from '../types';
import { isGroupBackgroundActionBusy } from '../utils';

interface DeliveryImportXlsxGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

type NullDeliveryPolicy = 'reset' | 'ignore';
type PaymentPlanGroupReconciliationImportFile = PaymentPlanImportFile & {
  override: boolean;
  null_delivery_policy: NullDeliveryPolicy;
};

export function DeliveryImportXlsxGroupButton({
  group,
}: DeliveryImportXlsxGroupButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const permissions = usePermissions();
  const [override, setOverride] = useState(false);
  const [nullDeliveryPolicy, setNullDeliveryPolicy] =
    useState<NullDeliveryPolicy>('reset');
  const canOverride = hasPermissions(
    PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION_OVERRIDE,
    permissions,
  );

  const resetOptions = (): void => {
    setOverride(false);
    setNullDeliveryPolicy('reset');
  };

  if (
    !hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX, permissions)
  )
    return null;

  return (
    <XlsxImportDialog<PaymentPlanGroupReconciliationImportFile>
      mutationFn={(formData) =>
        RestService.restBusinessAreasProgramsPaymentPlanGroupsDeliveryImportXlsxCreate(
          {
            businessAreaSlug: businessArea,
            id: group?.id,
            programCode: programId,
            formData,
          },
        )
      }
      invalidateQueryKey={restQueryKey(
        RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve,
      )}
      successMessage={t('Delivery reconciliation import started')}
      errorFallback={t('Import failed')}
      buttonLabel={t('Upload Reconciliation')}
      buttonVariant="contained"
      buttonMargin={2}
      disabled={!group || isGroupBackgroundActionBusy(group)}
      buildMutationVariables={(file) => ({
        file: file as unknown as string,
        override,
        null_delivery_policy: nullDeliveryPolicy,
      })}
      onReset={resetOptions}
      options={
        canOverride ? (
          <>
            <FormControlLabel
              control={
                <Checkbox
                  checked={override}
                  onChange={(event) => setOverride(event.target.checked)}
                />
              }
              label={t('This upload will overwrite existing matches')}
            />
            {override ? (
              <FormControl fullWidth margin="normal">
                <InputLabel id="null-delivery-policy-label">
                  {t('When delivered_quantity is empty')}
                </InputLabel>
                <Select
                  labelId="null-delivery-policy-label"
                  value={nullDeliveryPolicy}
                  label={t('When delivered_quantity is empty')}
                  onChange={(event) =>
                    setNullDeliveryPolicy(event.target.value)
                  }
                >
                  <MenuItem value="reset">
                    {t('Reset rows with empty/null delivered_quantity')}
                  </MenuItem>
                  <MenuItem value="ignore">
                    {t('Ignore rows with empty/null delivered_quantity')}
                  </MenuItem>
                </Select>
              </FormControl>
            ) : null}
          </>
        ) : null
      }
      dataCySuffix="delivery-import-xlsx-group"
    />
  );
}
