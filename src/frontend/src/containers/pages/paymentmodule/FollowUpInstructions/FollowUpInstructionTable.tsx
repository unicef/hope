import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/pages/paymentmodule/FollowUpInstructions/FollowUpInstructionHeadCells';
import { FollowUpInstructionTableRow } from '@containers/pages/paymentmodule/FollowUpInstructions/FollowUpInstructionTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTableState } from '@hooks/useTableState';
import { usePersistedCount } from '@hooks/usePersistedCount';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import type { FollowUpInstructionList } from '@restgenerated/models/FollowUpInstructionList';
import type { PaginatedFollowUpInstructionListList } from '@restgenerated/models/PaginatedFollowUpInstructionListList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import type { ReactElement } from 'react';

export const FollowUpInstructionTable = (): ReactElement => {
  const { businessArea, programId } = useBaseUrl();
  const table = useTableState();
  const { page } = table;

  const instructionsListParams = {
    businessAreaSlug: businessArea,
    programCode: programId,
    ...table.paginationParams,
  };
  const { data, isLoading, error } =
    useQuery<PaginatedFollowUpInstructionListList>({
      queryKey: restQueryKey(
        RestService.restBusinessAreasProgramsFollowUpInstructionsList,
        instructionsListParams,
      ),
      queryFn: () =>
        RestService.restBusinessAreasProgramsFollowUpInstructionsList(
          instructionsListParams,
        ),
      enabled: !!businessArea && !!programId,
      refetchInterval: (query) => {
        const results = query.state.data?.results ?? [];
        const hasPendingAction = results.some(
          (r) =>
            r.backgroundActionStatus !== null &&
            r.backgroundActionStatus !== '',
        );
        return hasPendingAction ? 3000 : false;
      },
      refetchIntervalInBackground: true,
    });

  const instructionsCountParams = {
    businessAreaSlug: businessArea,
    programCode: programId,
  };
  const { data: dataCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsFollowUpInstructionsCountRetrieve,
      instructionsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsFollowUpInstructionsCountRetrieve(
        instructionsCountParams,
      ),
    enabled: !!businessArea && !!programId && page === 0,
  });

  const itemsCount = usePersistedCount(page, dataCount);

  return (
    <UniversalRestTable
      title="Follow-up Instructions"
      headCells={headCells}
      tableState={table}
      data={data}
      error={error}
      isLoading={isLoading}
      itemsCount={itemsCount}
      renderRow={(row: FollowUpInstructionList) => (
        <FollowUpInstructionTableRow key={row.id} instruction={row} />
      )}
    />
  );
};
