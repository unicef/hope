import { Box, Button, Dialog, DialogActions, DialogTitle } from '@mui/material';
import { Publish } from '@mui/icons-material';
import get from 'lodash/get';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { ImportErrors } from '@containers/tables/payments/VerificationRecordsTable/errors/ImportErrors';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  ImportXlsxPpListPerFspMutation,
  PaymentPlanBackgroundActionStatus,
  PaymentPlanDocument,
  PaymentPlanQuery,
  useImportXlsxPpListPerFspMutation,
} from '@generated/graphql';
import { DropzoneField } from '@core/DropzoneField';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useProgramContext } from '../../../../programContext';
import { LoadingButton } from '@core/LoadingButton';

const Error = styled.div`
  color: ${({ theme }) => theme.palette.error.dark};
  padding: 20px;
`;

const UploadIcon = styled(Publish)`
  color: #043f91;
`;

const DisabledUploadIcon = styled(Publish)`
  color: #00000042;
`;

interface ImportXlsxPaymentPlanPaymentListPerFspProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  permissions: string[];
}

const allowedState = [
  null,
  PaymentPlanBackgroundActionStatus.XlsxExportError,
  PaymentPlanBackgroundActionStatus.XlsxImportError,
  PaymentPlanBackgroundActionStatus.RuleEngineError,
];

export function ImportXlsxPaymentPlanPaymentListPerFsp({
  paymentPlan,
  permissions,
}: ImportXlsxPaymentPlanPaymentListPerFspProps): ReactElement {
  const { showMessage } = useSnackbar();
  const [open, setOpenImport] = useState(false);
  const [fileToImport, setFileToImport] = useState(null);
  const { isActiveProgram } = useProgramContext();
  const { t } = useTranslation();

  const [mutate, { data: uploadData, loading: fileLoading, error }] =
    useImportXlsxPpListPerFspMutation();

  const xlsxErrors: ImportXlsxPpListPerFspMutation['importXlsxPaymentPlanPaymentListPerFsp']['errors'] =
    get(uploadData, 'importXlsxPaymentPlanPaymentListPerFsp.errors');
  const canUploadReconciliation =
    hasPermissions(
      PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION,
      permissions,
    ) && allowedState.includes(paymentPlan.backgroundActionStatus);

  const handleImport = async (): Promise<void> => {
    if (fileToImport) {
      try {
        const { data, errors } = await mutate({
          variables: {
            paymentPlanId: paymentPlan.id,
            file: fileToImport,
          },
          refetchQueries: () => [
            {
              query: PaymentPlanDocument,
              variables: {
                id: paymentPlan.id,
              },
            },
          ],
        });
        if (
          !errors &&
          !data?.importXlsxPaymentPlanPaymentListPerFsp.errors?.length
        ) {
          setOpenImport(false);
          showMessage(t('Your import was successful!'));
        }
      } catch (e) {
        e.graphQLErrors.map((x) => showMessage(x.message));
      }
    }
  };

  return (
    <>
      {canUploadReconciliation && paymentPlan.canSendToPaymentGateway && (
        <Box key="import">
          <Button
            startIcon={
              !isActiveProgram ? <DisabledUploadIcon /> : <UploadIcon />
            }
            color="primary"
            data-cy="button-import"
            onClick={() => setOpenImport(true)}
            disabled={!isActiveProgram}
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
            {fileToImport &&
            (error?.graphQLErrors?.length || xlsxErrors?.length) ? (
              <Error>
                <p>Errors</p>
                {error
                  ? error.graphQLErrors.map((x) => (
                      <p key={x.message}>{x.message}</p>
                    ))
                  : null}
                <ImportErrors errors={xlsxErrors} />
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
