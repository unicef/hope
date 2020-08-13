import React, { ReactElement } from 'react';
import {
  useAllPaymentVerificationsQuery,
  PaymentVerificationNodeEdge,
  AllPaymentVerificationsQueryVariables,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './VerificationRecordsHeadCells';
import { VerificationRecordsTableRow } from './VerificationRecordsTableRow';
import { Button, Box } from '@material-ui/core';
import { GetApp, Publish } from '@material-ui/icons';

export function VerificationRecordsTable({ id, filter }): ReactElement {
  const initialVariables: AllPaymentVerificationsQueryVariables = {
    cashPlanPaymentVerification: id,
  };

  const exportButton = (
    <Box mr={3}>
      <a href={`api/download_cash_plan_payment_verification/${id}`}>
        <Button
          startIcon={<GetApp />}
          color='primary'
          variant='outlined'
          onClick={() => console.log('EXPORT')}
          data-cy='button-submit'
        >
          EXPORT
        </Button>
      </a>
    </Box>
  );

  const importButton = (
    <Box>
      <Button
        startIcon={<Publish />}
        color='primary'
        variant='outlined'
        onClick={() => console.log('IMPORT')}
        data-cy='button-submit'
      >
        IMPORT
      </Button>
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
