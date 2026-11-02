import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { useQuery } from '@tanstack/react-query';
import { SanctionListIndividualsTableRow } from './SanctionListIndividualsTableRow';
import { headCells } from './SanctionListIndividualsHeadCells';
import type { PaginatedSanctionListIndividualList } from '@restgenerated/models/PaginatedSanctionListIndividualList';
import type { SanctionListIndividual } from '@restgenerated/models/SanctionListIndividual';
import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTableState } from '@hooks/useTableState';

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
  const filterVariables = useMemo(
    () => ({
      businessAreaSlug,
      fullName: filter.fullName || undefined,
      referenceNumber: filter.referenceNumber || undefined,
    }),
    [businessAreaSlug, filter.fullName, filter.referenceNumber],
  );
  const table = useTableState({ resetPageOn: filterVariables });
  const queryVariables = useMemo(
    () => ({ ...filterVariables, ...table.paginationParams }),
    [filterVariables, table.paginationParams],
  );

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
    <UniversalRestTable<SanctionListIndividual>
      title={''}
      headCells={headCells}
      tableState={table}
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
