import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { GetApp } from '@mui/icons-material';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogTitle,
  TextField,
} from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
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
  const [open, setOpen] = useState(false);
  const [fspTemplateId, setFspTemplateId] = useState('');
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync: exportBatch, isPending: loadingExport } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsDeliveryExportXlsxCreate(
        {
          businessAreaSlug: businessArea,
          programCode: programId,
          id: groupId,
          requestBody: {
            exportTag: parseInt(tag, 10),
            fspXlsxTemplateId: fspTemplateId || null,
          },
        },
      ),
    onSuccess: () => {
      showMessage(t('Export started'));
      queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroup', businessArea, programId, groupId],
      });
      setOpen(false);
      setFspTemplateId('');
    },
    onError: (error: any) => {
      showMessage(error?.message ?? t('Export failed'));
    },
  });

  const isDisabled = !groupId || !tag || loadingExport;

  return (
    <>
      <Box m={2}>
        <LoadingButton
          loading={loadingExport}
          startIcon={<GetApp />}
          color="primary"
          variant="contained"
          onClick={() => setOpen(true)}
          disabled={isDisabled}
          data-cy="button-export-batch"
        >
          {t('Re-export Batch')}
        </LoadingButton>
      </Box>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        maxWidth="sm"
        fullWidth
      >
        <DialogTitleWrapper data-cy="dialog-export-batch">
          <DialogTitle>{t('Re-export Batch #{{tag}}', { tag })}</DialogTitle>
          <TextField
            label={t('FSP XLSX Template ID (optional)')}
            value={fspTemplateId}
            onChange={(e) => setFspTemplateId(e.target.value)}
            fullWidth
            size="small"
            sx={{ mt: 1 }}
          />
          <DialogActions>
            <Button
              onClick={() => {
                setOpen(false);
                setFspTemplateId('');
              }}
            >
              {t('CANCEL')}
            </Button>
            <LoadingButton
              loading={loadingExport}
              color="primary"
              variant="contained"
              onClick={() => exportBatch()}
              data-cy="button-export-batch-submit"
            >
              {t('EXPORT')}
            </LoadingButton>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </>
  );
}
