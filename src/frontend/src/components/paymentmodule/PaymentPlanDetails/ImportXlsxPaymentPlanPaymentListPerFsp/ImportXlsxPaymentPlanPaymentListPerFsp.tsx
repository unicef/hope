import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { DropzoneField } from '@core/DropzoneField';
import { LoadingButton } from '@core/LoadingButton';
import XlsxErrorsDisplay from '@core/XlsxErrorsDisplay';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Publish } from '@mui/icons-material';
import { Box, Button, Dialog, DialogActions, DialogTitle } from '@mui/material';
import { BackgroundActionStatusEnum } from '@restgenerated/models/BackgroundActionStatusEnum';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { PaymentPlanImportFile } from '@restgenerated/models/PaymentPlanImportFile';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { getApiErrorMessages } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useProgramContext } from '../../../../programContext';

const UploadIcon = styled(Publish)`
  color: #043f91;
`;

const DisabledUploadIcon = styled(Publish)`
  color: #00000042;
`;

interface ImportXlsxPaymentPlanPaymentListPerFspProps {
  paymentPlan: PaymentPlanDetail;
  permissions: string[];
}

const allowedState = [
  null,
  BackgroundActionStatusEnum.XLSX_EXPORT_ERROR,
  BackgroundActionStatusEnum.XLSX_IMPORT_ERROR,
  BackgroundActionStatusEnum.RULE_ENGINE_ERROR,
];

export function ImportXlsxPaymentPlanPaymentListPerFsp({
  paymentPlan,
  permissions,
}: ImportXlsxPaymentPlanPaymentListPerFspProps): ReactElement {
  const { showMessage } = useSnackbar();
  const { businessArea, programId } = useBaseUrl();
  const [open, setOpenImport] = useState(false);
  const [fileToImport, setFileToImport] = useState(null);
  const [xlsxError, setXlsxError] = useState<string | null>(null);
  const { isActiveProgram } = useProgramContext();
  const { t } = useTranslation();
  const canUploadReconciliation =
    paymentPlan.status !== PaymentPlanStatusEnum.CLOSED &&
    hasPermissions(
      PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION,
      permissions,
    ) &&
    allowedState.includes(paymentPlan.backgroundActionStatus) &&
    paymentPlan.fspCommunicationChannel == 'XLSX';

  const { mutateAsync: importReconciliationXlsx, isPending: fileLoading } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        id,
        programSlug,
        formData,
      }: {
        businessAreaSlug: string;
        id: string;
        programSlug: string;
        formData: PaymentPlanImportFile;
      }) =>
        RestService.restBusinessAreasProgramsPaymentPlansReconciliationImportXlsxCreate(
          {
            businessAreaSlug,
            id,
            programSlug,
            formData,
          },
        ),
      onSuccess: () => {
        setOpenImport(false);
        showMessage(t('Your import was successful!'));
        setXlsxError(null);
      },
      onError: (error: any) => {
        setXlsxError(getApiErrorMessages(error));
      },
    });

  const handleImport = async (): Promise<void> => {
    if (fileToImport) {
      await importReconciliationXlsx({
        businessAreaSlug: businessArea,
        id: paymentPlan.id,
        programSlug: programId,
        formData: {
          file: fileToImport,
        },
      });
    }
  };

  return (
    <>
      {canUploadReconciliation && (
        <Box key="import">
          <Button
            startIcon={
              !isActiveProgram ? <DisabledUploadIcon /> : <UploadIcon />
            }
            color="primary"
            data-cy="button-import"
            onClick={() => setOpenImport(true)}
            disabled={!isActiveProgram}
            data-perm={PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION}
          >
            {t('Upload Reconciliation Info')}
          </Button>
        </Box>
      )}
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
            {fileToImport && xlsxError ? (
              <XlsxErrorsDisplay errors={xlsxError} data-cy="error-list" />
            ) : null}
          </>
          <DialogActions>
            <Button
              data-cy="close-button"
              onClick={() => {
                setOpenImport(false);
                setFileToImport(null);
                setXlsxError(null);
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
              data-cy="button-import-submit"
            >
              {t('IMPORT')}
            </LoadingButton>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </>
  );
}
