import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { DropzoneField } from '@core/DropzoneField';
import { LoadingButton } from '@core/LoadingButton';
import XlsxErrorsDisplay from '@core/XlsxErrorsDisplay';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Publish } from '@mui/icons-material';
import { Box, Button, Dialog, DialogActions, DialogTitle } from '@mui/material';
import { PaymentPlanImportFile } from '@restgenerated/models/PaymentPlanImportFile';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanGroupDetail } from '../types';

interface DeliveryImportXlsxGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function DeliveryImportXlsxGroupButton({
  group,
}: DeliveryImportXlsxGroupButtonProps): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [fileToImport, setFileToImport] = useState<File | null>(null);
  const [xlsxError, setXlsxError] = useState<string | null>(null);
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync, isPending } = useMutation({
    // TODO: backend endpoint `delivery-import-xlsx` is not yet merged.
    // POST /api/rest/{business_area_slug}/programs/{program_code}/payment-plan-groups/{id}/delivery-import-xlsx/
    // It synchronously validates the upload; on failure it returns 400 with a
    // list of { sheet, coordinates, message } (XlsxErrorSerializer), which
    // `getApiErrorMessages` + `XlsxErrorsDisplay` already render below.
    // When the backend lands:
    //   1. run `cd src/frontend && bun run generate-rest-api-types-camelcase`
    //      to regenerate RestService with the new method.
    //   2. uncomment the call below and delete the placeholder Promise.reject.
    //   3. import { RestService } from '@restgenerated/services/RestService';
    //   4. import { getApiErrorMessages } from '@utils/utils';
    //      and set `setXlsxError(getApiErrorMessages(error))` in onError.
    mutationFn: (_formData: PaymentPlanImportFile) =>
      // RestService.restBusinessAreasProgramsPaymentPlanGroupsDeliveryImportXlsxCreate({
      //   businessAreaSlug: businessArea,
      //   id: group?.id,
      //   programCode: programId,
      //   formData: _formData,
      // }),
      Promise.reject(
        new Error('delivery-import-xlsx endpoint not yet available'),
      ),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroup', businessArea, programId, group?.id],
      });
      setOpen(false);
      setFileToImport(null);
      setXlsxError(null);
      showMessage(t('Delivery reconciliation import started'));
    },
    onError: (error: any) => {
      // TODO: once the endpoint is merged, replace this with
      // setXlsxError(getApiErrorMessages(error)); to surface the
      // { sheet, coordinates, message } validation errors.
      setXlsxError(error?.message ?? t('Import failed'));
    },
  });

  const handleImport = async (): Promise<void> => {
    if (fileToImport) {
      await mutateAsync({ file: fileToImport as any });
    }
  };

  return (
    <>
      <Box m={2}>
        <Button
          startIcon={<Publish />}
          color="primary"
          variant="contained"
          onClick={() => setOpen(true)}
          disabled={!group}
          data-cy="button-delivery-import-xlsx-group"
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
        <DialogTitleWrapper data-cy="dialog-delivery-import-xlsx-group">
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
              data-cy="button-delivery-import-xlsx-group-submit"
            >
              {t('IMPORT')}
            </LoadingButton>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </>
  );
}
