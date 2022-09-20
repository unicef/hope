import React, { ReactElement } from 'react';
import { TableWrapper } from '../../../components/core/TableWrapper';
import {
  AllAccountabilityCommunicationMessagesQueryVariables,
  CommunicationMessageNode,
  useAllAccountabilityCommunicationMessagesQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './FeedbackTableHeadCells';
import { FeedbackTableRow } from './FeedbackTableRow';

interface FeedbackTableProps {
  filter;
  businessArea: string;
}

export const FeedbackTable = ({
  filter,
  businessArea,
}: FeedbackTableProps): ReactElement => {
  const initialVariables: AllAccountabilityCommunicationMessagesQueryVariables = {
    search: filter.search,
    status: filter.status,
    createdBy: filter.createdBy || '',
    createdAtRange: filter.createdAtRange
      ? JSON.stringify(filter.createdAtRange)
      : '',
    businessArea,
  };
  return (
    <TableWrapper>
      <UniversalTable<
        CommunicationMessageNode,
        AllAccountabilityCommunicationMessagesQueryVariables
      >
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllAccountabilityCommunicationMessagesQuery}
        queriedObjectName='allAccountabilityCommunicationMessages'
        defaultOrderBy='createdAt'
        defaultOrderDirection='desc'
        initialVariables={initialVariables}
        renderRow={(row) => <FeedbackTableRow key={row.id} feedback={row} />}
      />
    </TableWrapper>
  );
};
