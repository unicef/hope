import { Box, Button, Dialog, DialogActions, DialogTitle } from '@mui/material';
import { Publish } from '@mui/icons-material';
import get from 'lodash/get';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { ImportErrors } from '@containers/tables/payments/VerificationRecordsTable/errors/ImportErrors';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  ImportPeriodicDataUpdatesMutation,
  PaymentPlanDocument,
  PaymentPlanQuery,
  useImportPeriodicDataUpdatesMutation,
} from '@generated/graphql';
import { DropzoneField } from '@core/DropzoneField';
import { LoadingButton } from '@core/LoadingButton';
import { useProgramContext } from 'src/programContext';

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

export const PeriodDataUpdatesUploadDialog = (): React.ReactElement => {
  const { showMessage } = useSnackbar();
  const [open, setOpenImport] = useState(false);
  const [fileToImport, setFileToImport] = useState(null);
  const { isActiveProgram } = useProgramContext();
  const { t } = useTranslation();

  const [mutate, { data: uploadData, loading: fileLoading, error }] =
    useImportPeriodicDataUpdatesMutation();

  const xlsxErrors: ImportPeriodicDataUpdatesMutation['importPeriodicDataUpdates']['errors'] =
    get(uploadData, 'importPeriodicDataUpdates.errors');

  const handleImport = async (): Promise<void> => {
    //TODO MS: implement this function
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
        if (!errors && !data?.importPeriodicDataUpdates.errors?.length) {
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
      <Box key="import">
        <Button
          startIcon={!isActiveProgram ? <DisabledUploadIcon /> : <UploadIcon />}
          color="primary"
          data-cy="button-import"
          onClick={() => setOpenImport(true)}
          disabled={!isActiveProgram}
          endIcon={<UploadIcon />}
        >
          {t('Upload Data')}
        </Button>
      </Box>
      <Dialog
        open={open}
        onClose={() => setOpenImport(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper data-cy="dialog-import">
          <DialogTitle>{t('Periodic Data Updates')}</DialogTitle>
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
};
