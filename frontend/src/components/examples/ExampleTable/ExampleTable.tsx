import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllGrievanceTicketQuery,
  AllGrievanceTicketQueryVariables,
  useAllGrievanceTicketQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';
import { LoadingComponent } from '../../core/LoadingComponent';
import { TableWrapper } from '../../core/TableWrapper';
import { ExampleTableRow } from './ExampleTableRow';
import { headCells } from './ExampleTableHeadCells';

interface ExampleTableProps {
  filter?;
}

export const ExampleTable = ({
  filter,
}: ExampleTableProps): React.ReactElement => {
  const { businessArea } = useBaseUrl();
  const { t } = useTranslation();

  const initialVariables: AllGrievanceTicketQueryVariables = {
    businessArea,
  };

  const permissions = usePermissions();

  if (!permissions) {
    return null;
  }

  if (!filter) {
    return <LoadingComponent />;
  }

  return (
    <TableWrapper>
      <UniversalTable<
        AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'],
        AllGrievanceTicketQueryVariables
      >
        headCells={headCells}
        title={t('Example List')}
        rowsPerPageOptions={[10, 15, 20, 40]}
        query={useAllGrievanceTicketQuery}
        queriedObjectName='allGrievanceTicket'
        initialVariables={initialVariables}
        defaultOrderBy='created_at'
        defaultOrderDirection='desc'
        renderRow={(row) => <ExampleTableRow key={row.id} />}
      />
    </TableWrapper>
  );
};
