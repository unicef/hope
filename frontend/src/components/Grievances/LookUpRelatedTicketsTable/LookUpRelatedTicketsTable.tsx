import React from 'react';
import styled from 'styled-components';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import {
  AllGrievanceTicketQueryVariables,
  GrievanceTicketNode,
  useAllGrievanceTicketQuery,
} from '../../../__generated__/graphql';
import { headCells } from './LookUpRelatedTicketsHeadCells';
import { LookUpRelatedTicketsTableRow } from './LookUpRelatedTicketsTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface LookUpRelatedTicketsTableProps {
  businessArea: string;
  filter;
}

export const LookUpRelatedTicketsTable = ({
  businessArea,
  filter,
}: LookUpRelatedTicketsTableProps): React.ReactElement => {
  const initialVariables: AllGrievanceTicketQueryVariables = {
    businessArea,
    search: filter.search,
    status: [filter.status],
    fsp: [filter.fsp],
    createdAtRange: JSON.stringify(filter.createdAtRange),
    admin: [filter.admin],
  };

  return (
    <TableWrapper>
      <UniversalTable<GrievanceTicketNode, AllGrievanceTicketQueryVariables>
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllGrievanceTicketQuery}
        queriedObjectName='allGrievanceTicket'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <LookUpRelatedTicketsTableRow key={row.id} ticket={row} />
        )}
      />
    </TableWrapper>
  );
};
