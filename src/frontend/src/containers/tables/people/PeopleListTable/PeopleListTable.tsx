import { useTranslation } from 'react-i18next';
import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import type { IndividualList } from '@restgenerated/models/IndividualList';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import type { PaginatedIndividualListList } from '@restgenerated/models/PaginatedIndividualListList';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { headCells } from './PeopleListTableHeadCells';
import { PeopleListTableRow } from './PeopleListTableRow';
import type { ReactElement } from 'react';
import { useEffect, useMemo, useState } from 'react';
import { usePersistedCount } from '@hooks/usePersistedCount';
import type { CountResponse } from '@restgenerated/models/CountResponse';

interface PeopleListTableProps {
  filter;
  businessArea: string;
  canViewDetails: boolean;
}

export const PeopleListTable = ({
  businessArea,
  filter,
  canViewDetails,
}: PeopleListTableProps): ReactElement => {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();

  const [page, setPage] = useState(0);

  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programCode: programId,
      ageMax: filter.ageMax,
      ageMin: filter.ageMin,
      sex: [filter.sex],
      search: filter.search.trim(),
      documentType: filter.documentType,
      documentNumber: filter.documentNumber.trim(),
      admin1: [filter.admin1],
      admin2: [filter.admin2],
      flags: filter.flags,
      status: filter.status,
      lastRegistrationDateBefore: filter.lastRegistrationDateMin,
      lastRegistrationDateAfter: filter.lastRegistrationDateMax,
      rdiMergeStatus: 'MERGED',
      orderBy: filter.orderBy,
      rdiId: filter.rdiId,
      page,
    }),
    [
      filter.ageMin,
      filter.ageMax,
      filter.sex,
      filter.search,
      filter.documentType,
      filter.documentNumber,
      filter.admin1,
      filter.admin2,
      filter.flags,
      filter.status,
      filter.lastRegistrationDateMin,
      filter.lastRegistrationDateMax,
      filter.orderBy,
      programId,
      businessArea,
      page,
      filter.rdiId,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const individualsCountParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    queryVariables,
    { withPagination: true },
  );
  const { data: countData } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsIndividualsCountRetrieve,
      individualsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsCountRetrieve(
        individualsCountParams,
      ),
    enabled: page === 0,
  });

  const itemsCount = usePersistedCount(page, countData);

  const individualsListParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    queryVariables,
    { withPagination: true },
  );
  const { data, isLoading, isFetching, error } =
    useQuery<PaginatedIndividualListList>({
      queryKey: restQueryKey(
        RestService.restBusinessAreasProgramsIndividualsList,
        individualsListParams,
      ),
      queryFn: () =>
        RestService.restBusinessAreasProgramsIndividualsList(
          individualsListParams,
        ),
      placeholderData: keepPreviousData,
    });

  return (
    <TableWrapper>
      <UniversalRestTable
        title={t('People')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        data={data}
        error={error}
        isLoading={isLoading}
        isFetching={isFetching}
        allowSort={false}
        filterOrderBy={filter.orderBy}
        itemsCount={itemsCount}
        page={page}
        setPage={setPage}
        renderRow={(row: IndividualList) => (
          <PeopleListTableRow
            key={row.id}
            individual={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
};
