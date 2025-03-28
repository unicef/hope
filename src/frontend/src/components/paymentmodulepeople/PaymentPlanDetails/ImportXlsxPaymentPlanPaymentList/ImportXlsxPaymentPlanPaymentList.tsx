import { Box, Button, Dialog, DialogActions, DialogTitle } from '@mui/material';
import { Publish } from '@mui/icons-material';
import get from 'lodash/get';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { ImportErrors } from '@containers/tables/payments/VerificationRecordsTable/errors/ImportErrors';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  ImportXlsxPpListMutation,
  PaymentPlanDocument,
  PaymentPlanStatus,
  useImportXlsxPpListMutation,
} from '@generated/graphql';
import { DropzoneField } from '@core/DropzoneField';
import { useProgramContext } from '../../../../programContext';
import { LoadingButton } from '@core/LoadingButton';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

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

  const [mutate, { data: uploadData, loading: fileLoading, error }] =
    useImportXlsxPpListMutation();

  const xlsxErrors: ImportXlsxPpListMutation['importXlsxPaymentPlanPaymentList']['errors'] =
    get(uploadData, 'importXlsxPaymentPlanPaymentList.errors');

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
        if (!errors && !data?.importXlsxPaymentPlanPaymentList.errors?.length) {
          setOpenImport(false);
          showMessage(t('Your import was successful!'));
        }
      } catch (e) {
        e.graphQLErrors.map((x) => showMessage(x.message));
      }
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
            {fileToImport &&
            (error?.graphQLErrors?.length || xlsxErrors?.length) ? (
              <Error data-cy="error-list">
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
