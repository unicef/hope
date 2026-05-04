import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupsHeadCells';
import { PaymentPlanGroupTableRow } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedPaymentPlanGroupListList } from '@restgenerated/models/PaginatedPaymentPlanGroupListList';
import { PaymentPlanGroupList } from '@restgenerated/models/PaymentPlanGroupList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';

export const PaymentPlanGroupsTable = (): ReactElement => {
  const { businessArea, programId } = useBaseUrl();
  const [queryVariables, setQueryVariables] = useState({});
  const [page, setPage] = useState(0);

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

  return (
    <UniversalRestTable
      title="Groups"
      headCells={headCells}
      queryVariables={queryVariables}
      data={data}
      error={error}
      isLoading={isLoading}
      setQueryVariables={setQueryVariables}
      itemsCount={data?.count ?? 0}
      page={page}
      setPage={setPage}
      renderRow={(row: PaymentPlanGroupList) => (
        <PaymentPlanGroupTableRow key={row.id} group={row} />
      )}
    />
  );
};
