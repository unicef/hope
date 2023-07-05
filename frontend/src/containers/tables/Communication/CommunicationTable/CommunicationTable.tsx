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
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { useTranslation } from 'react-i18next';

interface CommunicationTableProps {
  filter;
  canViewDetails: boolean;
}

export const CommunicationTable = ({
  filter,
  canViewDetails,
}: CommunicationTableProps): ReactElement => {
  const { programId } = useBaseUrl();
  const { t } = useTranslation();
  const initialVariables: AllAccountabilityCommunicationMessagesQueryVariables = {
    createdAtRange: filter.createdAtRange
      ? JSON.stringify(filter.createdAtRange)
      : '',
    program: programId,
    targetPopulation: filter.targetPopulation,
    createdBy: filter.createdBy || '',
  };
  return (
    <TableWrapper>
      <UniversalTable<
        CommunicationMessageNode,
        AllAccountabilityCommunicationMessagesQueryVariables
      >
        title={t('Messages List')}
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
