import { PaymentPlanHeaderRow } from '@components/core/Table/PaymentPlanHeaderRow';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentListsHeadCells';
import { PaymentListTableRow } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentListTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { useTableState } from '@hooks/useTableState';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import type { PaginatedPaymentListListList } from '@restgenerated/models/PaginatedPaymentListListList';
import type { PaymentListList } from '@restgenerated/models/PaymentListList';
import type { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { RestService } from '@restgenerated/services/RestService';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { createApiParams } from '@utils/apiUtils';
import { adjustHeadCells } from '@utils/utils';
import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { useProgramContext } from 'src/programContext';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';

interface PaymentListsTableProps {
  programCycle?: ProgramCycleList;
  filter;
  canViewDetails: boolean;
  title?: string;
  paymentPlanId?: string;
}

export const PaymentListsTable = ({
  programCycle,
  filter,
  canViewDetails,
  title,
  paymentPlanId,
}: PaymentListsTableProps): ReactElement => {
  const { programId, businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const canViewList = hasPermissions(PERMISSIONS.PM_VIEW_LIST, permissions);
  const { selectedProgram, isSocialDctType } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const filterVariables = useMemo(
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
      paymentPlan: paymentPlanId,
      isPaymentList: true,
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
      paymentPlanId,
    ],
  );

  const table = useTableState({
    // Rows sit under a header per payment plan, so by default the plan sorts first.
    defaultOrdering: 'payment_plan_name,-created_at',
    resetPageOn: filterVariables,
  });
  const { page } = table;
  const listVariables = useMemo(
    () => ({
      ...filterVariables,
      ...table.paginationParams,
    }),
    [filterVariables, table.paginationParams],
  );

  const paymentListsParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    listVariables,
  );

  const {
    data: dataPaymentLists,
    isLoading: isLoadingPaymentLists,
    isFetching: isFetchingPaymentLists,
    error: errorPaymentLists,
  } = useQuery<PaginatedPaymentListListList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentListsList,
      paymentListsParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentListsList(paymentListsParams),
    placeholderData: keepPreviousData,
    enabled: canViewList && !!businessArea && !!programId,
  });

  const paymentListsCountParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    filterVariables,
  );

  const { data: dataPaymentListsCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentListsCountRetrieve,
      paymentListsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentListsCountRetrieve(
        paymentListsCountParams,
      ),
    enabled: canViewList && !!businessArea && !!programId && page === 0,
  });

  const replacements = {
    totalHouseholdsCount: (_beneficiaryGroup) =>
      isSocialDctType
        ? 'Num. of People'
        : `Num. of ${_beneficiaryGroup?.groupLabelPlural}`,
  };

  const itemsCount = usePersistedCount(page, dataPaymentListsCount);

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  const results = dataPaymentLists?.results ?? [];

  return (
    <UniversalRestTable
      title={title}
      headCells={adjustedHeadCells}
      tableState={table}
      data={dataPaymentLists}
      error={errorPaymentLists}
      isLoading={isLoadingPaymentLists}
      isFetching={isFetchingPaymentLists}
      itemsCount={itemsCount}
      renderRow={(row: PaymentListList) => {
        const idx = results.indexOf(row);
        const prev = results[idx - 1];
        const isNewPaymentPlan =
          idx === 0 || prev?.paymentPlan?.id !== row.paymentPlan?.id;
        return (
          <>
            {isNewPaymentPlan && (
              <PaymentPlanHeaderRow
                name={row.paymentPlan?.name}
                id={row.paymentPlan?.id}
              />
            )}
            <PaymentListTableRow
              key={row.id}
              paymentList={row}
              canViewDetails={canViewDetails}
            />
          </>
        );
      }}
    />
  );
};
