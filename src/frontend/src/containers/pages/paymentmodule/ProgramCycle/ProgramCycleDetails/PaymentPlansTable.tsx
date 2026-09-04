import { GroupHeaderRow } from '@components/core/Table/GroupHeaderRow';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansHeadCells';
import { PaymentPlanTableRow } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlanTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePersistedCount } from '@hooks/usePersistedCount';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import type { PaginatedPaymentPlanListList } from '@restgenerated/models/PaginatedPaymentPlanListList';
import type { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';
import type { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { RestService } from '@restgenerated/services/RestService';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { createApiParams } from '@utils/apiUtils';
import { adjustHeadCells } from '@utils/utils';
import type { ReactElement } from 'react';
import React, { useEffect, useState } from 'react';
import { useProgramContext } from 'src/programContext';

interface PaymentPlansTableProps {
  programCycle?: ProgramCycleList;
  filter;
  canViewDetails: boolean;
  title?: string;
  paymentPlanGroupId?: string;
  tag?: string;
}

export const PaymentPlansTable = ({
  programCycle,
  filter,
  canViewDetails,
  title,
  paymentPlanGroupId,
  tag,
}: PaymentPlansTableProps): ReactElement => {
  const { programId, businessArea } = useBaseUrl();
  const { selectedProgram, isSocialDctType } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const initialQueryVariables = React.useMemo(
    () => ({
      programCode: programId,
      businessAreaSlug: businessArea,
      search: filter.search,
      status: filter.status,
      totalEntitledQuantityFrom: filter.totalEntitledQuantityFrom,
      totalEntitledQuantityTo: filter.totalEntitledQuantityTo,
      dispersionStartDate: filter.dispersionStartDate,
      dispersionEndDate: filter.dispersionEndDate,
      planType: null,
      program: programId,
      programCycle: programCycle?.id,
      paymentPlanGroup: paymentPlanGroupId,
      exportTag: tag,
      isPaymentPlan: true,
    }),
    [
      businessArea,
      filter.search,
      filter.status,
      filter.totalEntitledQuantityFrom,
      filter.totalEntitledQuantityTo,
      filter.dispersionStartDate,
      filter.dispersionEndDate,
      programId,
      programCycle?.id,
      paymentPlanGroupId,
      tag,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const [page, setPage] = useState(0);

  const paymentPlansParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    queryVariables,
    { withPagination: true },
  );

  const {
    data: dataPaymentPlans,
    isLoading: isLoadingPaymentPlans,
    isFetching: isFetchingPaymentPlans,
    error: errorPaymentPlans,
  } = useQuery<PaginatedPaymentPlanListList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentPlansList,
      paymentPlansParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansList(paymentPlansParams),
    placeholderData: keepPreviousData,
    enabled: !!businessArea && !!programId,
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
      isSocialDctType
        ? 'Num. of People'
        : `Num. of ${_beneficiaryGroup?.groupLabelPlural}`,
  };

  const itemsCount = usePersistedCount(page, dataPaymentPlansCount);

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  const results = dataPaymentPlans?.results ?? [];

  return (
    <UniversalRestTable
      defaultOrderBy="paymentPlanGroup__name,-createdAt"
      title={title}
      headCells={adjustedHeadCells}
      queryVariables={queryVariables}
      data={dataPaymentPlans}
      error={errorPaymentPlans}
      isLoading={isLoadingPaymentPlans}
      isFetching={isFetchingPaymentPlans}
      setQueryVariables={setQueryVariables}
      itemsCount={itemsCount}
      page={page}
      setPage={setPage}
      renderRow={(row: PaymentPlanList) => {
        const idx = results.indexOf(row);
        const prev = results[idx - 1];
        const isNewGroup =
          idx === 0 || prev?.paymentPlanGroup?.id !== row.paymentPlanGroup?.id;
        return (
          <>
            {isNewGroup && (
              <GroupHeaderRow
                name={row.paymentPlanGroup?.name}
                id={row.paymentPlanGroup?.id}
              />
            )}
            <PaymentPlanTableRow
              key={row.id}
              paymentPlan={row}
              canViewDetails={canViewDetails}
            />
          </>
        );
      }}
    />
  );
};
