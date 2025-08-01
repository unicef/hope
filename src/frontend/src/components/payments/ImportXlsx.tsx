import { Box, Button, Dialog, DialogActions, DialogTitle } from '@mui/material';
import { Publish } from '@mui/icons-material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { DropzoneField } from '@core/DropzoneField';
import { LoadingButton } from '@core/LoadingButton';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { PaymentVerificationPlanImport } from '@restgenerated/models/PaymentVerificationPlanImport';

const Error = styled.div`
  color: ${({ theme }) => theme.palette.error.dark};
  padding: 20px;
`;

const StyledButton = styled(Button)`
  width: 150px;
`;

export interface ImportXlsxProps {
  paymentVerificationPlanId: string;
  cashOrPaymentPlanId: string;
}

export const ImportXlsx = ({
  paymentVerificationPlanId,
  cashOrPaymentPlanId,
}: ImportXlsxProps): ReactElement => {
  const { showMessage, showRestApiError } = useSnackbar();
  const { businessArea, programId: programSlug } = useBaseUrl();
  const [open, setOpenImport] = useState(false);
  const [fileToImport, setFileToImport] = useState(null);
  const queryClient = useQueryClient();
  const { t } = useTranslation();

  const importMutation = useMutation({
    mutationFn: (data: PaymentVerificationPlanImport) =>
      RestService.restBusinessAreasProgramsPaymentVerificationsImportXlsxCreate(
        {
          businessAreaSlug: businessArea,
          id: cashOrPaymentPlanId,
          programSlug: programSlug,
          verificationPlanId: paymentVerificationPlanId,
          formData: data,
        },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [
          'PaymentVerificationPlanDetails',
          businessArea,
          cashOrPaymentPlanId,
          programSlug,
        ],
      });
      queryClient.invalidateQueries({
        queryKey: [
          'businessAreasProgramsPaymentVerificationsVerificationsList',
        ],
      });
    },
  });

  const handleImport = async (): Promise<void> => {
    if (fileToImport) {
      try {

        await importMutation.mutateAsync({
          file: fileToImport,
        });
        setOpenImport(false);
        showMessage(t('Your import was successful!'));
      } catch (e) {
        showRestApiError(e);
      }
    }
  };
  const errorWithBody = importMutation.error as any;
  const errorBody = errorWithBody?.body;

  return (
    <>
      <Box key="import">
        <StyledButton
          startIcon={<Publish />}
          color="primary"
          variant="outlined"
          data-cy="button-import"
          onClick={() => setOpenImport(true)}
        >
          {t('Import XLSX')}
        </StyledButton>
      </Box>
      <Dialog
        open={open}
        onClose={() => setOpenImport(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Select File to Import')}</DialogTitle>
          <>
            <DropzoneField
              dontShowFilename={false}
              loading={importMutation.isPending}
              onChange={(files) => {
                if (files.length === 0) {
                  return;
                }
                const file = files[0];
                const fileSizeMB = file.size / (1024 * 1024);
                if (fileSizeMB > 200) {
                  showMessage(
                    `File size is too big. It should be under 200MB, File size is ${fileSizeMB}MB`,
                  );
                  return;
                }

                setFileToImport(file);
              }}
            />
            {fileToImport && importMutation.error && (
              <Error>
                <p>Errors</p>
                <p>{JSON.stringify(errorBody)}</p>
              </Error>
            )}
          </>
          <DialogActions>
            <Button
              onClick={() => {
                setOpenImport(false);
                setFileToImport(null);
              }}
            >
              CANCEL
            </Button>
            <LoadingButton
              loading={importMutation.isPending}
              disabled={!fileToImport}
              type="submit"
              color="primary"
              variant="contained"
              onClick={() => handleImport()}
              data-cy="button-import-entitlement"
            >
              {t('IMPORT')}
            </LoadingButton>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </>
  );
};
