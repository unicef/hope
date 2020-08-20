import React, { ReactElement, useState, useCallback } from 'react';
import styled from 'styled-components';
import get from 'lodash/get';
import { useTranslation } from 'react-i18next';
import {
  useAllPaymentVerificationsQuery,
  PaymentVerificationNodeEdge,
  AllPaymentVerificationsQueryVariables,
  useImportXlsxCashPlanVerificationMutation,
  ImportXlsxCashPlanVerificationMutation,
  XlsxErrorNode,
  ImportXlsxCashPlanVerificationMutationResult,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './VerificationRecordsHeadCells';
import { VerificationRecordsTableRow } from './VerificationRecordsTableRow';
import {
  Button,
  Box,
  makeStyles,
  DialogTitle,
  DialogContent,
} from '@material-ui/core';
import { GetApp, Publish } from '@material-ui/icons';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { Dialog } from '../../dialogs/Dialog';
import { DialogActions } from '../../dialogs/DialogActions';
import { DropzoneField } from '../../../components/DropzoneField';
import { ImportErrors } from './errors/ImportErrors';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const StyledDialogFooter = styled(DialogFooter)`
  && {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
`;

const Error = styled.div`
  color: ${({ theme }) => theme.palette.error.dark};
  padding: 20px;
`;

export function VerificationRecordsTable({
  id,
  verificationMethod,
  filter,
}): ReactElement {
  const { showMessage } = useSnackbar();
  const [open, setOpenImport] = useState(false);
  const [fileToImport, setFileToImport] = useState(null);
  const { t } = useTranslation();

  const initialVariables: AllPaymentVerificationsQueryVariables = {
    cashPlanPaymentVerification: id,
  };

  const useStyles = makeStyles(() => ({
    link: {
      textDecoration: 'none',
      '&:hover': {
        textDecoration: 'none',
        cursor: 'pointer',
      },
    },
  }));

  const classes = useStyles();

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
            cashPlanVerificationId: id,
            file: fileToImport,
          },
        });

        if (!errors && !data?.importXlsxCashPlanVerification?.errors.length) {
          setOpenImport(false);
          showMessage('Your import was successful!');
        }
      } catch (e) {
        console.error(e);
      }
    }
  };
  const exportButton =
    verificationMethod === 'XLSX' ? (
      <Box mr={3}>
        <a
          download
          className={classes.link}
          href={`/api/download-cash-plan-payment-verification/${id}`}
        >
          <Button
            startIcon={<GetApp />}
            color='primary'
            variant='outlined'
            data-cy='button-export'
          >
            EXPORT
          </Button>
        </a>
      </Box>
    ) : null;

  const importButton =
    verificationMethod === 'XLSX' ? (
      <Box>
        <Button
          startIcon={<Publish />}
          color='primary'
          variant='outlined'
          data-cy='button-import'
          onClick={() => setOpenImport(true)}
        >
          IMPORT
        </Button>
      </Box>
    ) : null;
  const importFile = (
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
          {error ? error.graphQLErrors.map((x) => <p>{x.message}</p>) : null}
          <ImportErrors errors={xlsxErrors as XlsxErrorNode[]} />
        </Error>
      ) : null}
    </>
  );

  return (
    <>
      <UniversalTable<
        PaymentVerificationNodeEdge,
        AllPaymentVerificationsQueryVariables
      >
        title='Verification Records'
        actions={[exportButton, importButton]}
        headCells={headCells}
        query={useAllPaymentVerificationsQuery}
        queriedObjectName='allPaymentVerifications'
        initialVariables={initialVariables}
        renderRow={(row) => <VerificationRecordsTableRow record={row} />}
      />
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
          {importFile}
          <DialogActions>
            <Button onClick={() => setOpenImport(false)}>CANCEL</Button>
            <Button
              disabled={!fileToImport}
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => handleImport()}
              data-cy='button-import'
            >
              {t('IMPORT')}
            </Button>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </>
  );
}
