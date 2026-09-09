import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupsHeadCells';
import { PaymentPlanGroupTableRow } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePersistedCount } from '@hooks/usePersistedCount';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import type { PaginatedPaymentPlanGroupListList } from '@restgenerated/models/PaginatedPaymentPlanGroupListList';
import type { PaymentPlanGroupList } from '@restgenerated/models/PaymentPlanGroupList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { createApiParams } from '@utils/apiUtils';
import type { ReactElement } from 'react';
import { useEffect, useState } from 'react';

interface PaymentPlanGroupsTableProps {
  filter?: { search?: string; cycle?: string };
}

export const PaymentPlanGroupsTable = ({
  filter,
}: PaymentPlanGroupsTableProps): ReactElement => {
  const { businessArea, programId } = useBaseUrl();
  const [queryVariables, setQueryVariables] = useState({
    businessAreaSlug: businessArea,
    programCode: programId,
  });
  const [page, setPage] = useState(0);

  useEffect(() => {
    setQueryVariables((prev) => ({
      ...prev,
      search: filter?.search || undefined,
      cycle: filter?.cycle || undefined,
    }));
    setPage(0);
  }, [filter]);

  const groupsListParams = {
    businessAreaSlug: businessArea,
    programCode: programId,
    ...queryVariables,
  };
  const { data, isLoading, error } =
    useQuery<PaginatedPaymentPlanGroupListList>({
      queryKey: restQueryKey(
        RestService.restBusinessAreasProgramsPaymentPlanGroupsList,
        groupsListParams,
      ),
      queryFn: () =>
        RestService.restBusinessAreasProgramsPaymentPlanGroupsList(
          groupsListParams,
        ),
      enabled: !!businessArea && !!programId,
    });

  const groupsCountParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    queryVariables,
  );
  const { data: dataCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentPlanGroupsCountRetrieve,
      groupsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsCountRetrieve(
        groupsCountParams,
      ),
    enabled: !!businessArea && !!programId && page === 0,
  });

  const itemsCount = usePersistedCount(page, dataCount);

  return (
    <UniversalRestTable
      title="Groups"
      headCells={headCells}
      queryVariables={queryVariables}
      data={data}
      error={error}
      isLoading={isLoading}
      setQueryVariables={setQueryVariables}
      itemsCount={itemsCount}
      page={page}
      setPage={setPage}
      renderRow={(row: PaymentPlanGroupList) => (
        <PaymentPlanGroupTableRow key={row.id} group={row} />
      )}
    />
  );
};
