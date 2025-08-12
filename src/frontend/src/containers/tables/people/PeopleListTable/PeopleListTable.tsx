import { useTranslation } from 'react-i18next';
import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { IndividualList } from '@restgenerated/models/IndividualList';
import { RestService } from '@restgenerated/services/RestService';
import { PaginatedIndividualListList } from '@restgenerated/models/PaginatedIndividualListList';
import { useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { headCells } from './PeopleListTableHeadCells';
import { PeopleListTableRow } from './PeopleListTableRow';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { CountResponse } from '@restgenerated/models/CountResponse';

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

  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programSlug: programId,
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
      programId,
      businessArea,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);
  const { data: countData } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsHouseholdsCount',
      programId,
      businessArea,
      queryVariables,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsCountRetrieve(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
          { withPagination: true },
        ),
      ),
  });

  const { data, isLoading, error } = useQuery<PaginatedIndividualListList>({
    queryKey: [
      'businessAreasProgramsIndividualsList',
      queryVariables,
      businessArea,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
          { withPagination: true },
        ),
      ),
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
        allowSort={false}
        filterOrderBy={filter.orderBy}
        itemsCount={countData?.count}
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
