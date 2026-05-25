import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { GetApp } from '@mui/icons-material';
import { Box } from '@mui/material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanGroupDetail } from '../types';

interface DeliveryExportXlsxGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function DeliveryExportXlsxGroupButton({
  group,
}: DeliveryExportXlsxGroupButtonProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync: exportXlsx, isPending: loadingExport } = useMutation({
    // TODO: backend endpoint `delivery-export-xlsx` is not yet merged.
    // POST /api/rest/{business_area_slug}/programs/{program_code}/payment-plan-groups/{id}/delivery-export-xlsx/
    // When the backend lands:
    //   1. run `cd src/frontend && bun run generate-rest-api-types-camelcase`
    //      to regenerate RestService with the new method.
    //   2. uncomment the call below and delete the placeholder Promise.reject.
    //   3. import { RestService } from '@restgenerated/index';
    mutationFn: () =>
      // RestService.restBusinessAreasProgramsPaymentPlanGroupsDeliveryExportXlsxCreate({
      //   businessAreaSlug: businessArea,
      //   programCode: programId,
      //   id: group?.id,
      // }),
      Promise.reject(
        new Error('delivery-export-xlsx endpoint not yet available'),
      ),
    onSuccess: () => {
      showMessage(t('Export started'));
      queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroup', businessArea, programId, group?.id],
      });
    },
    onError: (error: any) => {
      showMessage(error?.message ?? t('Export failed'));
    },
  });

  const isDisabled = !group || loadingExport;

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
