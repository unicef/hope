import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { useQuery } from '@tanstack/react-query';
import { SanctionListIndividualsTableRow } from './SanctionListIndividualsTableRow';
import { headCells } from './SanctionListIndividualsHeadCells';
import type { PaginatedSanctionListIndividualList } from '@restgenerated/models/PaginatedSanctionListIndividualList';
import type { SanctionListIndividual } from '@restgenerated/models/SanctionListIndividual';
import type { ReactElement } from 'react';
import { useMemo, useState, useEffect } from 'react';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface SanctionListIndividualsTableProps {
  filter: {
    fullName?: string;
    referenceNumber?: string;
    [key: string]: any;
  };
}

export function SanctionListIndividualsTable({
  filter,
}: SanctionListIndividualsTableProps): ReactElement {
  const { businessAreaSlug } = useBaseUrl();
  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug,
      fullName: filter.fullName || undefined,
      referenceNumber: filter.referenceNumber || undefined,
    }),
    [businessAreaSlug, filter.fullName, filter.referenceNumber],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const [page, setPage] = useState(0);

  const { data, isLoading, error } =
    useQuery<PaginatedSanctionListIndividualList>({
      queryKey: restQueryKey(
        RestService.restBusinessAreasSanctionListList,
        queryVariables,
      ),
      queryFn: () =>
        RestService.restBusinessAreasSanctionListList({ ...queryVariables }),
    });

  return (
    <UniversalRestTable<SanctionListIndividual, typeof queryVariables>
      title={''}
      headCells={headCells}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      data={data}
      isLoading={isLoading}
      error={error}
      itemsCount={data?.results?.length}
      page={page}
      setPage={setPage}
      renderRow={(row: SanctionListIndividual) => (
        <SanctionListIndividualsTableRow key={row.id} individual={row} />
      )}
    />
  );
}
