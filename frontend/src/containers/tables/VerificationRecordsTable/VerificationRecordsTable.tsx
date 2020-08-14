import React, { ReactElement, useState } from 'react';
import {
  useAllPaymentVerificationsQuery,
  PaymentVerificationNodeEdge,
  AllPaymentVerificationsQueryVariables,
  useImportXlsxCashPlanVerificationMutation,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './VerificationRecordsHeadCells';
import { VerificationRecordsTableRow } from './VerificationRecordsTableRow';
import { Button, Box, makeStyles } from '@material-ui/core';
import { GetApp, Publish } from '@material-ui/icons';
import { UploadButton } from '../../../components/UploadButton';
import { useSnackbar } from '../../../hooks/useSnackBar';

export function VerificationRecordsTable({ id, filter }): ReactElement {
  const { showMessage } = useSnackbar();
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

  const [mutate] = useImportXlsxCashPlanVerificationMutation();

  const onFileUploadHandler = async (file): Promise<void> => {
    try {
      await mutate({
        variables: {
          cashPlanVerificationId: id,
          file,
        },
      });
    } catch (e) {
      console.log('🦀', e.message);
      console.log(e.graphQLErrors.map((x) => x.message));
      e.graphQLErrors.map((x) => console.log(x.message));
      return;
    }
    showMessage('Your XLSX import has been successful');
  };

  const exportButton = (
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
          data-cy='button-submit'
        >
          EXPORT
        </Button>
      </a>
    </Box>
  );

  const importButton = (
    <Box>
      <UploadButton
        startIcon={<Publish />}
        color='primary'
        variant='outlined'
        handleChange={onFileUploadHandler}
        data-cy='button-submit'
      >
        IMPORT
      </UploadButton>
    </Box>
  );

  return (
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
  );
}
