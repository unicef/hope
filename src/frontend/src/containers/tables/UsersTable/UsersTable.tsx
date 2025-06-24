import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { headCells } from './UsersTableHeadCells';
import { UsersTableRow } from './UsersTableRow';
import { PaginatedUserList } from '@restgenerated/models/PaginatedUserList';
import { RestService } from '@restgenerated/services/RestService';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useQuery } from '@tanstack/react-query';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { filterEmptyParams } from '@utils/utils';
interface UsersTableProps {
  filter;
}

export const UsersTable = ({ filter }: UsersTableProps): ReactElement => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();

  const initialQueryVariables = useMemo(
    () => ({
      search: filter.search,
      partner: filter.partner,
      roles: filter.roles,
      status: filter.status,
      businessAreaSlug: businessArea,
      program: programId,
      limit: 10,
      offset: 0,
      serializer: 'program_users',
    }),
    [
      filter.search,
      filter.partner,
      filter.roles,
      filter.status,
      businessArea,
      programId,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const filteredQueryVariables = useMemo(() => {
    const filtered = filterEmptyParams(initialQueryVariables);
    return {
      ...filtered,
      businessAreaSlug: businessArea,
      offset: queryVariables.offset,
      limit: queryVariables.limit,
    };
  }, [initialQueryVariables, queryVariables, businessArea]);

  const {
    data: dataUsers,
    isLoading: isLoadingUsers,
    error: errorUsers,
  } = useQuery<PaginatedUserList>({
    queryKey: ['businessAreasUsersList', filteredQueryVariables],
    queryFn: () =>
      RestService.restBusinessAreasUsersList(filteredQueryVariables),
  });

  const { data: dataUsersCount } = useQuery<CountResponse>({
    queryKey: ['businessAreasUsersCount', businessArea, filteredQueryVariables],
    queryFn: () =>
      RestService.restBusinessAreasUsersCountRetrieve(filteredQueryVariables),
  });

  return (
    <TableWrapper>
      <UniversalRestTable
        title={t('Users List')}
        headCells={headCells}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        data={dataUsers}
        isLoading={isLoadingUsers}
        error={errorUsers}
        itemsCount={dataUsersCount?.count}
        rowsPerPageOptions={[10, 15, 20]}
        defaultOrderBy="status"
        defaultOrderDirection="desc"
        renderRow={(row) => <UsersTableRow user={row} key={row.id} />}
      />
    </TableWrapper>
  );
};
