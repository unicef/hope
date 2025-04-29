import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { DropzoneField } from '@core/DropzoneField';
import { LoadingButton } from '@core/LoadingButton';
import { PaymentPlanStatus } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Publish } from '@mui/icons-material';
import { Box, Button, Dialog, DialogActions, DialogTitle } from '@mui/material';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { PaymentPlanImportFile } from '@restgenerated/models/PaymentPlanImportFile';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useProgramContext } from '../../../../programContext';

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

  const {
    mutateAsync: importEntitlementXlsx,
    isPending: fileLoading,
    error: xlsxErrors,
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
      RestService.restBusinessAreasProgramsPaymentPlansEntitlementImportXlsxCreate(
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
    },
    onError: (e) => {
      showMessage(e.message);
    },
  });

  const handleImport = async (): Promise<void> => {
    if (fileToImport) {
      await importEntitlementXlsx({
        businessAreaSlug: businessArea,
        id: paymentPlan.id,
        programSlug: programId,
        requestBody: {
          //TODO:
          //@ts-ignore
          file: fileToImport,
        },
      });
    }
  };

  const canUploadFile = hasPermissions(
    PERMISSIONS.PM_IMPORT_XLSX_WITH_ENTITLEMENTS,
    permissions,
  );

  const shouldDisableUpload =
    paymentPlan.status !== PaymentPlanStatus.Locked ||
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
            {fileToImport && xlsxErrors ? (
              <Error data-cy="error-list">
                <p>Errors</p>
                <p>{xlsxErrors.message}</p>
                {/* //TODO: fix */}
                {/* <ImportErrors errors={xlsxErrors} /> */}
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
