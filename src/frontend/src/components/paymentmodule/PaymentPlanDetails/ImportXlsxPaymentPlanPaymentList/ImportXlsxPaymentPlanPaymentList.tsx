import { Box, Button, Dialog, DialogActions, DialogTitle } from '@mui/material';
import { Publish } from '@mui/icons-material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '@hooks/useSnackBar';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { PaymentPlanImportFile } from '@restgenerated/models/PaymentPlanImportFile';
import { RestService } from '@restgenerated/services/RestService';
import { DropzoneField } from '@core/DropzoneField';
import { useProgramContext } from '../../../../programContext';
import { LoadingButton } from '@core/LoadingButton';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';

const Error = styled.div`
  color: ${({ theme }) => theme.palette.error.dark};
  padding: 20px;
`;

interface ImportXlsxPaymentPlanPaymentListProps {
  paymentPlan: PaymentPlanDetail;
  permissions: string[];
}

export function ImportXlsxPaymentPlanPaymentList({
  paymentPlan,
  permissions,
}: ImportXlsxPaymentPlanPaymentListProps): ReactElement {
  const { showMessage } = useSnackbar();
  const [open, setOpenImport] = useState(false);
  const [fileToImport, setFileToImport] = useState<File | null>(null);
  const { isActiveProgram } = useProgramContext();
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const queryClient = useQueryClient();

  const {
    mutateAsync: mutate,
    isPending: fileLoading,
    error,
  } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      id,
      programSlug,
      requestBody,
    }: {
      businessAreaSlug: string;
      id: string;
      programSlug: string;
      requestBody: PaymentPlanImportFile;
    }) =>
      RestService.restBusinessAreasProgramsPaymentPlansReconciliationImportXlsxCreate(
        {
          businessAreaSlug,
          id,
          programSlug,
          requestBody,
        },
      ),
    onSuccess: () => {
      setOpenImport(false);
      showMessage(t('Your import was successful!'));
      // Invalidate payment plan queries to refetch updated data
      queryClient.invalidateQueries({
        queryKey: ['paymentPlan', paymentPlan.id],
      });
    },
    onError: (e) => {
      showMessage(e.message || 'An error occurred during import');
    },
  });

  const handleImport = async (): Promise<void> => {
    if (fileToImport) {
      try {
        await mutate({
          businessAreaSlug: businessArea,
          id: paymentPlan.id,
          programSlug: programId,
          requestBody: {
            // @ts-ignore - File object is expected here despite the string type in the model
            file: fileToImport,
          },
        });
      } catch (e) {
        // Error is already handled by onError in mutation
      }
    }
  };

  const canUploadFile = hasPermissions(
    PERMISSIONS.PM_IMPORT_XLSX_WITH_ENTITLEMENTS,
    permissions,
  );

  const shouldDisableUpload =
    paymentPlan.status !== PaymentPlanStatusEnum.LOCKED ||
    !canUploadFile ||
    !isActiveProgram;

  return (
    <>
      <Box key="import">
        <Button
          startIcon={<Publish />}
          color="primary"
          data-cy="button-import"
          onClick={() => setOpenImport(true)}
          disabled={shouldDisableUpload}
        >
          {t('Upload File')}
        </Button>
      </Box>
      <Dialog
        open={open}
        onClose={() => setOpenImport(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper data-cy="dialog-import">
          <DialogTitle>{t('Select File to Import')}</DialogTitle>
          <>
            <DropzoneField
              dontShowFilename={false}
              loading={fileLoading}
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
            {fileToImport && error ? (
              <Error data-cy="error-list">
                <p>Errors</p>
                <p>{error.message}</p>
              </Error>
            ) : null}
          </>
          <DialogActions>
            <Button
              data-cy="close-button"
              onClick={() => {
                setOpenImport(false);
                setFileToImport(null);
              }}
            >
              CANCEL
            </Button>
            <LoadingButton
              loading={fileLoading}
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
}
