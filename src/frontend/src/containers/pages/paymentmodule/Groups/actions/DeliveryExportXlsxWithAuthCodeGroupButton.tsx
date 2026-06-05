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
import { PaymentPlanGroupDetail } from '../types';

interface DeliveryExportXlsxWithAuthCodeGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function DeliveryExportXlsxWithAuthCodeGroupButton({
  group,
}: DeliveryExportXlsxWithAuthCodeGroupButtonProps): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [fspTemplateId, setFspTemplateId] = useState('');
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync: exportXlsx, isPending: loadingExport } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsDeliveryExportXlsxWithAuthCodeCreate(
        {
          businessAreaSlug: businessArea,
          programCode: programId,
          id: group?.id,
          requestBody: {
            fspXlsxTemplateId: fspTemplateId || null,
          },
        },
      ),
    onSuccess: () => {
      showMessage(t('Export started'));
      queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroup', businessArea, programId, group?.id],
      });
      setOpen(false);
      setFspTemplateId('');
    },
    onError: (error: any) => {
      showMessage(error?.message ?? t('Export failed'));
    },
  });

  return (
    <>
      <Box m={2}>
        <Button
          startIcon={<GetApp />}
          color="primary"
          variant="outlined"
          onClick={() => setOpen(true)}
          disabled={!group}
          data-cy="button-delivery-export-xlsx-with-auth-code-group"
        >
          {t('Export with Auth Code')}
        </Button>
      </Box>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        maxWidth="sm"
        fullWidth
      >
        <DialogTitleWrapper data-cy="dialog-delivery-export-xlsx-with-auth-code-group">
          <DialogTitle>{t('Export with Auth Code')}</DialogTitle>
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
              onClick={() => exportXlsx()}
              data-cy="button-delivery-export-xlsx-with-auth-code-group-submit"
            >
              {t('EXPORT')}
            </LoadingButton>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </>
  );
}
