import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { DropzoneField } from '@core/DropzoneField';
import { LoadingButton } from '@core/LoadingButton';
import XlsxErrorsDisplay from '@core/XlsxErrorsDisplay';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Publish } from '@mui/icons-material';
import { Box, Button, Dialog, DialogActions, DialogTitle } from '@mui/material';
import { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import { PaymentPlanImportFile } from '@restgenerated/models/PaymentPlanImportFile';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { getApiErrorMessages } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';

interface ReconciliationImportButtonProps {
  instruction: FollowUpInstructionDetail;
}

export function ReconciliationImportButton({
  instruction,
}: ReconciliationImportButtonProps): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [fileToImport, setFileToImport] = useState<File | null>(null);
  const [xlsxError, setXlsxError] = useState<string | null>(null);
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync, isPending } = useMutation({
    mutationFn: (formData: PaymentPlanImportFile) =>
      RestService.restBusinessAreasProgramsFollowUpInstructionsDeliveryImportXlsxCreate(
        {
          businessAreaSlug: businessArea,
          id: instruction.id,
          programCode: programId,
          formData,
        },
      ),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: [
          'followUpInstruction',
          businessArea,
          instruction.id,
          programId,
        ],
      });
      setOpen(false);
      setFileToImport(null);
      setXlsxError(null);
      showMessage(t('Reconciliation import started'));
    },
    onError: (error: any) => {
      setXlsxError(getApiErrorMessages(error));
    },
  });

  const handleImport = async (): Promise<void> => {
    if (fileToImport) {
      await mutateAsync({ file: fileToImport as any });
    }
  };

  return (
    <>
      <Box>
        <Button
          startIcon={<Publish />}
          color="primary"
          onClick={() => setOpen(true)}
          data-cy="button-reconciliation-import"
        >
          {t('Upload Reconciliation')}
        </Button>
      </Box>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        maxWidth="sm"
        fullWidth
      >
        <DialogTitleWrapper data-cy="dialog-reconciliation-import">
          <DialogTitle>{t('Select File to Import')}</DialogTitle>
          <>
            <DropzoneField
              dontShowFilename={false}
              loading={isPending}
              onChange={(files) => {
                if (files.length === 0) return;
                const file = files[0];
                const fileSizeMB = file.size / (1024 * 1024);
                if (fileSizeMB > 200) {
                  showMessage(
                    t(
                      `File size is too big. It should be under 200MB, File size is ${fileSizeMB}MB`,
                    ),
                  );
                  return;
                }
                setFileToImport(file);
              }}
            />
            {fileToImport && xlsxError ? (
              <XlsxErrorsDisplay errors={xlsxError} />
            ) : null}
          </>
          <DialogActions>
            <Button
              onClick={() => {
                setOpen(false);
                setFileToImport(null);
                setXlsxError(null);
              }}
            >
              {t('CANCEL')}
            </Button>
            <LoadingButton
              loading={isPending}
              disabled={!fileToImport}
              color="primary"
              variant="contained"
              onClick={handleImport}
              data-cy="button-reconciliation-import-submit"
            >
              {t('IMPORT')}
            </LoadingButton>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </>
  );
}
