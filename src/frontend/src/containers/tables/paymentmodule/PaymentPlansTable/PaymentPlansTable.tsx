import type { ReactElement } from 'react';
import { Fragment, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaymentPlanTableRow } from './PaymentPlanTableRow';
import { headCells, headCellsPeople } from './PaymentPlansHeadCells';
import { useProgramContext } from 'src/programContext';
import { adjustHeadCells } from '@utils/utils';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { createApiParams } from '@utils/apiUtils';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { RestService } from '@restgenerated/services/RestService';
import type { PaginatedPaymentPlanListList } from '@restgenerated/models/PaginatedPaymentPlanListList';
import type { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { GroupHeaderRow } from '@components/core/Table/GroupHeaderRow';

interface PaymentPlansTableProps {
  filter;
  canViewDetails: boolean;
}

function PaymentPlansTable({
  filter,
  canViewDetails,
}: PaymentPlansTableProps): ReactElement {
  const { t } = useTranslation();
  const { programId, businessArea } = useBaseUrl();
  const { selectedProgram, isSocialDctType } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programCode: programId,
      search: filter.search,
      status: filter.status,
      totalEntitledQuantityUsdFrom: filter.totalEntitledQuantityUsdFrom || null,
      totalEntitledQuantityUsdTo: filter.totalEntitledQuantityUsdTo || null,
      dispersionStartDate: filter.dispersionStartDate || null,
      dispersionEndDate: filter.dispersionEndDate || null,
      planType: filter.planType,
      isPaymentPlan: true,
    }),
    [
      businessArea,
      programId,
      filter.search,
      filter.status,
      filter.totalEntitledQuantityUsdFrom,
      filter.totalEntitledQuantityUsdTo,
      filter.dispersionStartDate,
      filter.dispersionEndDate,
      filter.planType,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const [page, setPage] = useState(0);

  const paymentPlansListParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    queryVariables,
    { withPagination: true },
  );
  const {
    data: paymentPlansData,
    isLoading,
    isFetching,
    error,
  } = useQuery<PaginatedPaymentPlanListList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentPlansList,
      paymentPlansListParams,
    ),
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentPlansList(
        paymentPlansListParams,
      );
    },
    placeholderData: keepPreviousData,
  });

  const paymentPlansCountParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    queryVariables,
  );
  const { data: dataPaymentPlansCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentPlansCountRetrieve,
      paymentPlansCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansCountRetrieve(
        paymentPlansCountParams,
      ),
    enabled: !!businessArea && !!programId && page === 0,
  });

  const replacements = {
    totalHouseholdsCount: (_beneficiaryGroup) =>
      `Num. of ${_beneficiaryGroup?.groupLabelPlural}`,
  };

  const itemsCount = usePersistedCount(page, dataPaymentPlansCount);

  const adjustedHeadCells = isSocialDctType
    ? headCellsPeople
    : adjustHeadCells(headCells, beneficiaryGroup, replacements);

  // Ids of the first row in each consecutive group, so the group header renders
  // exactly once per group boundary (computed once instead of per-row indexOf).
  const groupStartRowIds = useMemo(() => {
    const ids = new Set<string>();
    const rows = paymentPlansData?.results ?? [];
    rows.forEach((row, idx) => {
      const prev = rows[idx - 1];
      if (
        idx === 0 ||
        prev?.paymentPlanGroup?.id !== row.paymentPlanGroup?.id
      ) {
        ids.add(row.id);
      }
    });
    return ids;
  }, [paymentPlansData]);

  return (
    <UniversalRestTable
      defaultOrderBy="paymentPlanGroup__name,-createdAt"
      title={t('Payment Plans')}
      headCells={adjustedHeadCells as any}
      data={paymentPlansData}
      isLoading={isLoading}
      isFetching={isFetching}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      itemsCount={itemsCount}
      page={page}
      setPage={setPage}
      renderRow={(row: PaymentPlanList) => (
        <Fragment key={row.id}>
          {groupStartRowIds.has(row.id) && (
            <GroupHeaderRow
              name={row.paymentPlanGroup?.name}
              id={row.paymentPlanGroup?.id}
            />
          )}
          <PaymentPlanTableRow plan={row} canViewDetails={canViewDetails} />
        </Fragment>
      )}
    />
  );
}

export default withErrorBoundary(PaymentPlansTable, 'PaymentPlansTable');
