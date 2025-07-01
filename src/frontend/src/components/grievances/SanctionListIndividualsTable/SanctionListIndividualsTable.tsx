import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { SanctionListIndividualsTableRow } from './SanctionListIndividualsTableRow';
import { headCells } from './SanctionListIndividualsHeadCells';
import { PaginatedSanctionListIndividualList } from '@restgenerated/models/PaginatedSanctionListIndividualList';
import { SanctionListIndividual } from '@restgenerated/models/SanctionListIndividual';
import { ReactElement, useMemo, useState, useEffect } from 'react';
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

  const { data, isLoading, error } =
    useQuery<PaginatedSanctionListIndividualList>({
      queryKey: ['restSanctionListList', queryVariables],
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
      renderRow={(row: SanctionListIndividual) => (
        <SanctionListIndividualsTableRow key={row.id} individual={row} />
      )}
    />
  );
}
