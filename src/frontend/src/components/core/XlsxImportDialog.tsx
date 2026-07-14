import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { DropzoneField } from '@core/DropzoneField';
import { LoadingButton } from '@core/LoadingButton';
import XlsxErrorsDisplay from '@core/XlsxErrorsDisplay';
import { useSnackbar } from '@hooks/useSnackBar';
import { Publish } from '@mui/icons-material';
import { Box, Button, Dialog, DialogActions, DialogTitle } from '@mui/material';
import { PaymentPlanImportFile } from '@restgenerated/models/PaymentPlanImportFile';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { getApiErrorMessages } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';

const MAX_FILE_SIZE_MB = 200;

interface XlsxImportDialogProps {
  /** Wires the actual import endpoint; receives the multipart form data. */
  mutationFn: (formData: PaymentPlanImportFile) => Promise<unknown>;
  /** Query key invalidated on a successful import. */
  invalidateQueryKey: unknown[];
  successMessage: string;
  /** Fallback message when the API error has no parsable body. */
  errorFallback?: string;
  buttonLabel: string;
  buttonVariant?: 'text' | 'contained';
  /** `m` spacing applied to the trigger button's wrapping Box. */
  buttonMargin?: number;
  disabled?: boolean;
  /** Base suffix, e.g. `delivery-import-xlsx-group` → `button-delivery-import-xlsx-group`. */
  dataCySuffix: string;
}

/**
 * Shared "select an XLSX file and import it" dialog used by reconciliation
 * uploads on both Follow-up Instructions and Payment Plan Groups.
 */
export function XlsxImportDialog({
  mutationFn,
  invalidateQueryKey,
  successMessage,
  errorFallback,
  buttonLabel,
  buttonVariant = 'text',
  buttonMargin = 0,
  disabled = false,
  dataCySuffix,
}: XlsxImportDialogProps): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [fileToImport, setFileToImport] = useState<File | null>(null);
  const [xlsxError, setXlsxError] = useState<string | null>(null);
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync, isPending } = useMutation({
    mutationFn,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: invalidateQueryKey });
      setOpen(false);
      setFileToImport(null);
      setXlsxError(null);
      showMessage(successMessage);
    },
    onError: (error) => {
      setXlsxError(getApiErrorMessages(error, errorFallback));
    },
  });

  const handleImport = async (): Promise<void> => {
    if (fileToImport) {
      // The generated PaymentPlanImportFile types `file` as string, but the
      // endpoint expects the File for multipart upload.
      await mutateAsync({ file: fileToImport as unknown as string });
    }
  };

  const handleClose = (): void => {
    setOpen(false);
    setFileToImport(null);
    setXlsxError(null);
  };

  return (
    <>
      <Box m={buttonMargin}>
        <Button
          startIcon={<Publish />}
          color="primary"
          variant={buttonVariant}
          onClick={() => setOpen(true)}
          disabled={disabled}
          data-cy={`button-${dataCySuffix}`}
        >
          {buttonLabel}
        </Button>
      </Box>
      <Dialog
        open={open}
        onClose={handleClose}
        scroll="paper"
        maxWidth="sm"
        fullWidth
      >
        <DialogTitleWrapper data-cy={`dialog-${dataCySuffix}`}>
          <DialogTitle>{t('Select File to Import')}</DialogTitle>
          <>
            <DropzoneField
              dontShowFilename={false}
              loading={isPending}
              onChange={(files) => {
                if (files.length === 0) return;
                const file = files[0];
                const fileSizeMB = file.size / (1024 * 1024);
                if (fileSizeMB > MAX_FILE_SIZE_MB) {
                  showMessage(
                    t(
                      'File size is too big. It should be under {{max}}MB, file size is {{size}}MB',
                      { max: MAX_FILE_SIZE_MB, size: fileSizeMB.toFixed(1) },
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
            <Button onClick={handleClose}>{t('CANCEL')}</Button>
            <LoadingButton
              loading={isPending}
              disabled={!fileToImport}
              color="primary"
              variant="contained"
              onClick={handleImport}
              data-cy={`button-${dataCySuffix}-submit`}
            >
              {t('IMPORT')}
            </LoadingButton>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </>
  );
}
