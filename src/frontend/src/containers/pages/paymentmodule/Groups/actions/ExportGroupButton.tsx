import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { GetApp } from '@mui/icons-material';
import { Box } from '@mui/material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanGroupDetail } from '../types';

interface ExportGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function ExportGroupButton({
  group,
}: ExportGroupButtonProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync: exportGroup, isPending: loadingExport } = useMutation({
    mutationFn: () =>
      // TODO (TICKET-8): implement once backend adds the export action
      // RestService.restBusinessAreasProgramsPaymentPlanGroupsExportCreate({
      //   businessAreaSlug: businessArea, programCode: programId, id: group!.id,
      // })
      Promise.reject(new Error('Export endpoint not yet available')),
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
        onClick={() => exportGroup()}
        disabled={isDisabled}
        data-cy="button-export-group"
      >
        {t('Export')}
      </LoadingButton>
    </Box>
  );
}
