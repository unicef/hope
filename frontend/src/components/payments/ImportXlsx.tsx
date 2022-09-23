import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogTitle,
} from '@material-ui/core';
import { Publish } from '@material-ui/icons';
import get from 'lodash/get';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { ImportErrors } from '../../containers/tables/payments/VerificationRecordsTable/errors/ImportErrors';
import { usePaymentRefetchQueries } from '../../hooks/usePaymentRefetchQueries';
import { useSnackbar } from '../../hooks/useSnackBar';
import {
  useImportXlsxCashPlanVerificationMutation,
  ImportXlsxCashPlanVerificationMutation,
  XlsxErrorNode,
} from '../../__generated__/graphql';
import { DropzoneField } from '../core/DropzoneField';

const Error = styled.div`
  color: ${({ theme }) => theme.palette.error.dark};
  padding: 20px;
`;

const StyledButton = styled(Button)`
  width: 150px;
`;

export function ImportXlsx({ verificationPlanId, cashPlanId }): ReactElement {
  const refetchQueries = usePaymentRefetchQueries(cashPlanId);
  const { showMessage } = useSnackbar();
  const [open, setOpenImport] = useState(false);
  const [fileToImport, setFileToImport] = useState(null);

  const { t } = useTranslation();

  const [
    mutate,
    { data: uploadData, loading: fileLoading, error },
  ] = useImportXlsxCashPlanVerificationMutation();

  const xlsxErrors: ImportXlsxCashPlanVerificationMutation['importXlsxCashPlanVerification']['errors'] = get(
    uploadData,
    'importXlsxCashPlanVerification.errors',
  );

  const handleImport = async (): Promise<void> => {
    if (fileToImport) {
      try {
        const { data, errors } = await mutate({
          variables: {
            cashPlanVerificationId: verificationPlanId,
            file: fileToImport,
          },
          refetchQueries,
        });

        if (!errors && !data?.importXlsxCashPlanVerification?.errors.length) {
          setOpenImport(false);
          showMessage(t('Your import was successful!'));
        }
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error(e);
      }
    }
  };

  return (
    <>
      <Box key='import'>
        <StyledButton
          startIcon={<Publish />}
          color='primary'
          variant='outlined'
          data-cy='button-import'
          onClick={() => setOpenImport(true)}
        >
          {t('Import XLSX')}
        </StyledButton>
      </Box>
      <Dialog
        open={open}
        onClose={() => setOpenImport(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            {t('Select File to Import')}
          </DialogTitle>
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
            {error?.graphQLErrors?.length || xlsxErrors?.length ? (
              <Error>
                <p>Errors</p>
                {error
                  ? error.graphQLErrors.map((x) => <p>{x.message}</p>)
                  : null}
                <ImportErrors errors={xlsxErrors as XlsxErrorNode[]} />
              </Error>
            ) : null}
          </>
          <DialogActions>
            <Button onClick={() => setOpenImport(false)}>CANCEL</Button>
            <Button
              disabled={!fileToImport}
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => handleImport()}
              data-cy='button-import-entitlement'
            >
              {t('IMPORT')}
            </Button>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </>
  );
}
