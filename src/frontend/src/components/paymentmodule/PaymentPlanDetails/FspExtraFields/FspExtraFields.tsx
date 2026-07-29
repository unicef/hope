import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { DropzoneField } from '@core/DropzoneField';
import { LoadingButton } from '@core/LoadingButton';
import { Title } from '@core/Title';
import XlsxErrorsDisplay from '@core/XlsxErrorsDisplay';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { GetApp, Publish } from '@mui/icons-material';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogTitle,
  Grid,
  Typography,
} from '@mui/material';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { PaymentPlanImportFile } from '@restgenerated/models/PaymentPlanImportFile';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { getApiErrorMessages } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useProgramContext } from '../../../../programContext';

interface FspExtraFieldsProps {
  paymentPlan: PaymentPlanDetail;
  permissions: string[];
}

export function FspExtraFields({
  paymentPlan,
  permissions,
}: FspExtraFieldsProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [xlsxError, setXlsxError] = useState<string | null>(null);

  const { mutateAsync: importFile, isPending } = useMutation({
    mutationFn: (requestBody: PaymentPlanImportFile) =>
      RestService.restBusinessAreasProgramsPaymentPlansFspExtraFieldsImportXlsxCreate(
        {
          businessAreaSlug: businessArea,
          programCode: programId,
          id: paymentPlan.id,
          formData: requestBody,
        },
      ),
    onSuccess: () => {
      setOpen(false);
      setFile(null);
      setXlsxError(null);
      showMessage(t('FSP extra fields import started.'));
      queryClient.invalidateQueries({
        queryKey: ['paymentPlan', businessArea, paymentPlan.id, programId],
      });
    },
    onError: (error: any) => {
      setXlsxError(getApiErrorMessages(error));
    },
  });

  const canImport = hasPermissions(
    PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION,
    permissions,
  );
  const actionsDisabled = !isActiveProgram;

  const handleImport = async (): Promise<void> => {
    if (!file) return;
    await importFile({
      // @ts-ignore File is required for multipart upload despite the generated string type.
      file,
    });
  };

  return (
    <Box sx={{ m: 5 }}>
      <ContainerColumnWithBorder>
        <Box sx={{ mt: 4 }}>
          <Title>
            <Typography variant="h6">{t('FSP Extra Fields')}</Typography>
          </Title>
          <Typography color="textSecondary">
            {t(
              'Download the Payment Record template, add FSP-required columns, and upload it before approval.',
            )}
          </Typography>
        </Box>
        <Grid container spacing={3} sx={{ py: 4 }}>
          <Grid size={{ xs: 6 }} sx={{ textAlign: 'center' }}>
            <Button
              component="a"
              download
              startIcon={<GetApp />}
              disabled={actionsDisabled}
              href={`/api/rest/business-areas/${businessArea}/programs/${programId}/payment-plans/${paymentPlan.id}/fsp-extra-fields-template/`}
            >
              {t('Download Template')}
            </Button>
          </Grid>
          <Grid size={{ xs: 6 }} sx={{ textAlign: 'center' }}>
            <Button
              startIcon={<Publish />}
              disabled={actionsDisabled || !canImport}
              data-perm={PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION}
              onClick={() => setOpen(true)}
            >
              {t('Upload File')}
            </Button>
          </Grid>
        </Grid>
      </ContainerColumnWithBorder>
      <Dialog open={open} onClose={() => setOpen(false)} scroll="paper">
        <DialogTitleWrapper>
          <DialogTitle>{t('Select FSP Extra Fields File')}</DialogTitle>
          <DropzoneField
            dontShowFilename={false}
            loading={isPending}
            onChange={(files) => {
              if (!files.length) return;
              const selectedFile = files[0];
              if (selectedFile.size > 200 * 1024 * 1024) {
                showMessage(
                  t('File size is too big. It should be under 200MB.'),
                );
                return;
              }
              setFile(selectedFile);
              setXlsxError(null);
            }}
          />
          {file && xlsxError ? <XlsxErrorsDisplay errors={xlsxError} /> : null}
          <DialogActions>
            <Button
              onClick={() => {
                setOpen(false);
                setFile(null);
                setXlsxError(null);
              }}
            >
              {t('Cancel')}
            </Button>
            <LoadingButton
              loading={isPending}
              disabled={!file}
              variant="contained"
              onClick={handleImport}
            >
              {t('Import')}
            </LoadingButton>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </Box>
  );
}
