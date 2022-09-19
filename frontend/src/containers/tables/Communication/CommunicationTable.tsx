import React, { ReactElement } from 'react';
import { TableWrapper } from '../../../components/core/TableWrapper';
import {
  AllCommunicationMessagesQueryVariables,
  MessageNode,
  useAllCommunicationMessagesQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './CommunicationTableHeadCells';
import { CommunicationTableRow } from './CommunicationTableRow';

interface CommunicationProps {
  filter;
  businessArea: string;
}

export const CommunicationTable = ({
  filter,
  businessArea,
}: CommunicationProps): ReactElement => {
  const initialVariables: AllCommunicationMessagesQueryVariables = {
    createdAtRange: JSON.stringify(filter.createdAtRange),
    program: filter.program,
    targetPopulation: filter.targetPopulation,
    createdBy: filter.createdBy || '',
    businessArea,
  };
  return (
    <TableWrapper>
      <UniversalTable<MessageNode, AllCommunicationMessagesQueryVariables>
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllCommunicationMessagesQuery}
        queriedObjectName='allCommunicationMessages'
        defaultOrderBy='createdAt'
        defaultOrderDirection='desc'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <CommunicationTableRow
            key={row.id}
            message={row}
          />
        )}
      />
    </TableWrapper>
  );
};
