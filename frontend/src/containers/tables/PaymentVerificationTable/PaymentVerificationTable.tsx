import React, { ReactElement } from 'react';
import styled from 'styled-components';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './PaymentVerificationHeadCells'
import { PaymentVerificationTableRow } from './PaymentVerificationTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface PaymentVerificationProps {
  id?: string;
  query?;
  queryObjectName?;
  variables?;
  filter;
}

export const PaymentVerificationTable = ({
  id,
  query,
  queryObjectName,
  variables,
  filter
}: PaymentVerificationProps): ReactElement => {
  const initialVariables = {
    ...(id && { targetPopulation: id }),
    ...variables,
    name: filter.name
  };
  return (
    <TableWrapper>
      <UniversalTable
        title='List of Cash Plans'
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={query}
        queriedObjectName={queryObjectName}
        initialVariables={initialVariables}
        renderRow={(row) => (
          <PaymentVerificationTableRow plan={row} />
        )}
      />
    </TableWrapper>
  );
};
