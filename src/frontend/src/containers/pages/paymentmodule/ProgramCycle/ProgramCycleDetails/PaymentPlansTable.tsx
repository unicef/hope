import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansHeadCells';
import { PaymentPlanTableRow } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlanTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { PaginatedPaymentPlanListList } from '@restgenerated/models/PaginatedPaymentPlanListList';
import { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells } from '@utils/utils';
import React, { ReactElement, useEffect, useState } from 'react';
import { useProgramContext } from 'src/programContext';

interface PaymentPlansTableProps {
  programCycle: ProgramCycleList;
  filter;
  canViewDetails: boolean;
  title?: string;
}

export const PaymentPlansTable = ({
  programCycle,
  filter,
  canViewDetails,
  title,
}: PaymentPlansTableProps): ReactElement => {
  const { programId, businessArea } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const initialQueryVariables = React.useMemo(
    () => ({
      programSlug: programId,
      businessAreaSlug: businessArea,
      search: filter.search,
      status: filter.status,
      totalEntitledQuantityFrom: filter.totalEntitledQuantityFrom,
      totalEntitledQuantityTo: filter.totalEntitledQuantityTo,
      dispersionStartDate: filter.dispersionStartDate,
      dispersionEndDate: filter.dispersionEndDate,
      isFollowUp: null,
      program: programId,
      programCycle: programCycle.id,
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
      programCycle.id,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const {
    data: dataPaymentPlans,
    isLoading: isLoadingPaymentPlans,
    error: errorPaymentPlans,
  } = useQuery<PaginatedPaymentPlanListList>({
    queryKey: [
      'businessAreasPaymentPlans',
      queryVariables,
      programId,
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansList(queryVariables),
    enabled: !!businessArea && !!programId,
  });

  const { data: dataPaymentPlansCount } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsPaymentPlansCountRetrieve',
      queryVariables,
      programId,
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansCountRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
      }),
  });

  const replacements = {
    totalHouseholdsCount: (_beneficiaryGroup) =>
      `Num. of ${_beneficiaryGroup?.groupLabelPlural}`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  return (
    <UniversalRestTable
      defaultOrderBy="-createdAt"
      title={title}
      headCells={adjustedHeadCells}
      queryVariables={queryVariables}
      data={dataPaymentPlans}
      error={errorPaymentPlans}
      isLoading={isLoadingPaymentPlans}
      setQueryVariables={setQueryVariables}
      itemsCount={dataPaymentPlansCount?.count}
      renderRow={(row: PaymentPlanList) => (
        <PaymentPlanTableRow
          key={row.id}
          paymentPlan={row}
          canViewDetails={canViewDetails}
        />
      )}
    />
  );
};
