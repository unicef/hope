import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllUsersQueryVariables,
  useAllUsersQuery,
  UserNode,
} from '../../../__generated__/graphql';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './UsersTableHeadCells';
import { UsersTableRow } from './UsersTableRow';

interface UsersTableProps {
  filter;
}

export const UsersTable = ({ filter }: UsersTableProps): ReactElement => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();

  const initialVariables = {
    search: filter.search,
    partner: filter.partner,
    roles: filter.roles,
    status: filter.status,
    businessArea,
  };
  return (
    <TableWrapper>
      <UniversalTable<UserNode, AllUsersQueryVariables>
        title={t('Users List')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllUsersQuery}
        queriedObjectName='allUsers'
        defaultOrderBy='status'
        defaultOrderDirection='desc'
        initialVariables={initialVariables}
        renderRow={(row) => <UsersTableRow user={row} key={row.id} />}
      />
    </TableWrapper>
  );
};
