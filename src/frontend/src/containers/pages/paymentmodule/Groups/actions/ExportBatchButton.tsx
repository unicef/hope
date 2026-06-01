import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { GetApp } from '@mui/icons-material';
import { Box } from '@mui/material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

interface ExportBatchButtonProps {
  groupId: string;
  tag: string;
}

export function ExportBatchButton({
  groupId,
  tag,
}: ExportBatchButtonProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync: exportBatch, isPending: loadingExport } = useMutation({
    // TODO: dedicated batch export endpoint is not yet merged.
    // A batch is (group id + tag), so the endpoint is expected to be scoped by
    // both. When the backend lands:
    //   1. run `cd src/frontend && bun run generate-rest-api-types-camelcase`
    //      to regenerate RestService with the new method.
    //   2. uncomment the call below and delete the placeholder Promise.reject.
    //   3. import { RestService } from '@restgenerated/services/RestService';
    mutationFn: () =>
      // RestService.restBusinessAreasProgramsPaymentPlanGroupsBatchExportXlsxCreate({
      //   businessAreaSlug: businessArea,
      //   programCode: programId,
      //   id: groupId,
      //   tag,
      // }),
      Promise.reject(new Error('batch export endpoint not yet available')),
    onSuccess: () => {
      showMessage(t('Export started'));
      queryClient.invalidateQueries({
        queryKey: ['batch', businessArea, programId, groupId, tag],
      });
    },
    onError: (error: any) => {
      showMessage(error?.message ?? t('Export failed'));
    },
  });

  const isDisabled = !groupId || !tag || loadingExport;

  return (
    <Box m={2}>
      <LoadingButton
        loading={loadingExport}
        startIcon={<GetApp />}
        color="primary"
        variant="contained"
        onClick={() => exportBatch()}
        disabled={isDisabled}
        data-cy="button-export-batch"
      >
        {t('Export Batch')}
      </LoadingButton>
    </Box>
  );
}
