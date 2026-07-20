import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { GetApp } from '@mui/icons-material';
import { Box } from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { PaymentPlanGroupDetail } from '../types';
import { isGroupBackgroundActionBusy } from '../utils';
import { showApiErrorMessages } from '@utils/utils';

interface DeliveryExportXlsxGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function DeliveryExportXlsxGroupButton({
  group,
}: DeliveryExportXlsxGroupButtonProps): ReactElement | null {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const permissions = usePermissions();

  const { mutateAsync: exportXlsx, isPending: loadingExport } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsDeliveryExportXlsxCreate(
        {
          businessAreaSlug: businessArea,
          programCode: programId,
          id: group?.id,
        },
      ),
    onSuccess: () => {
      showMessage(t('Export started'));
      queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroup', businessArea, programId, group?.id],
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage, t('Export failed'));
    },
  });

  if (
    !hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX, permissions)
  )
    return null;

  const isDisabled =
    !group || loadingExport || isGroupBackgroundActionBusy(group);

  return (
    <Box m={2}>
      <LoadingButton
        loading={loadingExport}
        startIcon={<GetApp />}
        color="primary"
        variant="contained"
        onClick={() => exportXlsx()}
        disabled={isDisabled}
        data-cy="button-delivery-export-xlsx-group"
      >
        {t('Export')}
      </LoadingButton>
    </Box>
  );
}
