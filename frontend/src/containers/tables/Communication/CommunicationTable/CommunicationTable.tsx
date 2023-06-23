import React, { ReactElement } from 'react';
import { TableWrapper } from '../../../../components/core/TableWrapper';
import {
  AllAccountabilityCommunicationMessagesQueryVariables,
  CommunicationMessageNode,
  useAllAccountabilityCommunicationMessagesQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './CommunicationTableHeadCells';
import { CommunicationTableRow } from './CommunicationTableRow';

interface CommunicationTableProps {
  filter;
  canViewDetails: boolean;
}

export const CommunicationTable = ({
  filter,
  canViewDetails,
}: CommunicationTableProps): ReactElement => {
  const initialVariables: AllAccountabilityCommunicationMessagesQueryVariables = {
    createdAtRange: filter.createdAtRange
      ? JSON.stringify(filter.createdAtRange)
      : '',
    program: filter.program,
    targetPopulation: filter.targetPopulation,
    createdBy: filter.createdBy || '',
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
        renderRow={(row) => (
          <CommunicationTableRow
            key={row.id}
            message={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
};
