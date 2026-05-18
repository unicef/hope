import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupsHeadCells';
import { PaymentPlanGroupTableRow } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { PaginatedPaymentPlanGroupListList } from '@restgenerated/models/PaginatedPaymentPlanGroupListList';
import { PaymentPlanGroupList } from '@restgenerated/models/PaymentPlanGroupList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { ReactElement, useEffect, useState } from 'react';

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

  const { data, isLoading, error } = useQuery<PaginatedPaymentPlanGroupListList>({
    queryKey: ['paymentPlanGroupsList', businessArea, programId, queryVariables],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsList({
        businessAreaSlug: businessArea,
        programCode: programId,
        ...queryVariables,
      }),
    enabled: !!businessArea && !!programId,
  });

  const { data: dataCount } = useQuery<CountResponse>({
    queryKey: ['paymentPlanGroupsCount', businessArea, programId, queryVariables],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsCountRetrieve(
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
