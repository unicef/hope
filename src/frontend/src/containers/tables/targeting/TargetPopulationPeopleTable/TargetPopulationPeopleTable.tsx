import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { headCells } from './TargetPopulationPeopleHeadCells';
import { TargetPopulationPeopleTableRow } from './TargetPopulationPeopleRow';
import { createApiParams } from '@utils/apiUtils';
import { PaginatedPendingPaymentList } from '@restgenerated/models/PaginatedPendingPaymentList';
import { PendingPayment } from '@restgenerated/models/PendingPayment';

interface TargetPopulationPeopleTableProps {
  id?: string;
  variables?;
  canViewDetails?: boolean;
}

export function TargetPopulationPeopleTable({
  id,
  variables,
  canViewDetails,
}: TargetPopulationPeopleTableProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const initialQueryVariables = useMemo(
    () => ({
      ...variables,
      businessAreaSlug: businessArea,
      programCode: programId,
      targetPopulationId: id,
    }),
    [variables, businessArea, programId, id],
  );
  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const pendingPaymentsListParams = createApiParams(
    {
      businessAreaSlug: businessArea,
      programCode: programId,
      id,
    },
    queryVariables,
    { withPagination: true },
  );
  const {
    data: householdsData,
    isLoading,
    isFetching,
    error,
  } = useQuery<PaginatedPendingPaymentList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsTargetPopulationsPendingPaymentsList,
      pendingPaymentsListParams,
    ),
    queryFn: () => {
      return RestService.restBusinessAreasProgramsTargetPopulationsPendingPaymentsList(
        pendingPaymentsListParams,
      );
    },
    placeholderData: keepPreviousData,
  });

  return (
    <TableWrapper>
      <UniversalRestTable
        title={t('People')}
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        isLoading={isLoading}
        isFetching={isFetching}
        error={error}
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        data={householdsData}
        renderRow={(row: PendingPayment) => (
          <TargetPopulationPeopleTableRow
            key={row.id}
            payment={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
}
