import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/pages/paymentmodule/FollowUpInstructions/FollowUpInstructionHeadCells';
import { FollowUpInstructionTableRow } from '@containers/pages/paymentmodule/FollowUpInstructions/FollowUpInstructionTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { FollowUpInstructionList } from '@restgenerated/models/FollowUpInstructionList';
import { PaginatedFollowUpInstructionListList } from '@restgenerated/models/PaginatedFollowUpInstructionListList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { ReactElement, useState } from 'react';

export const FollowUpInstructionTable = (): ReactElement => {
  const { businessArea, programId } = useBaseUrl();
  const [queryVariables, setQueryVariables] = useState({
    businessAreaSlug: businessArea,
    programCode: programId,
  });
  const [page, setPage] = useState(0);

  const { data, isLoading, error } =
    useQuery<PaginatedFollowUpInstructionListList>({
      queryKey: [
        'followUpInstructionsList',
        businessArea,
        programId,
        queryVariables,
      ],
      queryFn: () =>
        RestService.restBusinessAreasProgramsFollowUpInstructionsList({
          businessAreaSlug: businessArea,
          programCode: programId,
          ...queryVariables,
        }),
      enabled: !!businessArea && !!programId,
      refetchInterval: (query) => {
        const results = query.state.data?.results ?? [];
        const hasPendingAction = results.some(
          (r) => r.backgroundActionStatus !== null && r.backgroundActionStatus !== '',
        );
        return hasPendingAction ? 3000 : false;
      },
      refetchIntervalInBackground: true,
    });

  const { data: dataCount } = useQuery<CountResponse>({
    queryKey: [
      'followUpInstructionsCount',
      businessArea,
      programId,
      queryVariables,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsFollowUpInstructionsCountRetrieve(
        createApiParams(
          { businessAreaSlug: businessArea, programCode: programId },
          queryVariables,
        ),
      ),
    enabled: !!businessArea && !!programId && page === 0,
  });

  const itemsCount = usePersistedCount(page, dataCount);

  return (
    <UniversalRestTable
      title="Follow-up Instructions"
      headCells={headCells}
      queryVariables={queryVariables}
      data={data}
      error={error}
      isLoading={isLoading}
      setQueryVariables={setQueryVariables}
      itemsCount={itemsCount}
      page={page}
      setPage={setPage}
      renderRow={(row: FollowUpInstructionList) => (
        <FollowUpInstructionTableRow key={row.id} instruction={row} />
      )}
    />
  );
};
