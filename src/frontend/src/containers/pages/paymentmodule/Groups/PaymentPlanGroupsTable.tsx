import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupsHeadCells';
import { PaymentPlanGroupTableRow } from '@containers/pages/paymentmodule/Groups/PaymentPlanGroupTableRow';
import { ReactElement, useState } from 'react';

interface Group {
  id: string;
  unicefId: string;
  name: string;
  cycle: string;
}

// TODO: Replace with RestService call once endpoint is available:
// RestService.restBusinessAreasPaymentPlanGroupsList({ businessAreaSlug })
const useGroupsQuery = () => ({
  data: { count: 0, next: null, previous: null, results: [] as Group[] },
  isLoading: false,
  error: null,
});

export const PaymentPlanGroupsTable = (): ReactElement => {
  const [queryVariables, setQueryVariables] = useState({});
  const [page, setPage] = useState(0);

  const { data, isLoading, error } = useGroupsQuery();

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
      renderRow={(row: Group) => (
        <PaymentPlanGroupTableRow key={row.id} group={row} />
      )}
    />
  );
};
