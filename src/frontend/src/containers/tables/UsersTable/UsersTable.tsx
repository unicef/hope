import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTableState } from '@hooks/useTableState';
import { headCells } from './UsersTableHeadCells';
import { UsersTableRow } from './UsersTableRow';
import type { PaginatedUserList } from '@restgenerated/models/PaginatedUserList';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useQuery } from '@tanstack/react-query';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import { createApiParams } from '@utils/apiUtils';
import { usePersistedCount } from '@hooks/usePersistedCount';
interface UsersTableProps {
  filter;
}

export const UsersTable = ({ filter }: UsersTableProps): ReactElement => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();

  const filterVariables = useMemo(
    () => ({
      search: filter.search,
      partner: filter.partner,
      roles: filter.roles,
      status: filter.status,
      program: programId,
      serializer: 'program_users',
    }),
    [filter.search, filter.partner, filter.roles, filter.status, programId],
  );

  const table = useTableState({
    rowsPerPageOptions: [10, 15, 20],
    defaultOrderBy: 'status',
    defaultOrderDirection: 'desc',
    resetPageOn: filterVariables,
  });
  const { page } = table;
  const usersListParams = createApiParams(
    { businessAreaSlug: businessArea },
    { ...filterVariables, ...table.paginationParams },
  );
  const usersCountParams = createApiParams(
    { businessAreaSlug: businessArea },
    filterVariables,
  );

  const {
    data: dataUsers,
    isLoading: isLoadingUsers,
    error: errorUsers,
  } = useQuery<PaginatedUserList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasUsersList,
      usersListParams,
    ),
    queryFn: () => RestService.restBusinessAreasUsersList(usersListParams),
  });

  const { data: dataUsersCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasUsersCountRetrieve,
      usersCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasUsersCountRetrieve(usersCountParams),
    enabled: page === 0,
  });

  const persistedCount = usePersistedCount(page, dataUsersCount);

  return (
    <TableWrapper>
      <UniversalRestTable
        title={t('Users List')}
        headCells={headCells}
        tableState={table}
        data={dataUsers}
        isLoading={isLoadingUsers}
        error={errorUsers}
        itemsCount={persistedCount}
        renderRow={(row) => <UsersTableRow user={row} key={row.id} />}
      />
    </TableWrapper>
  );
};
