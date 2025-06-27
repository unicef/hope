import React, { ReactElement } from 'react';
import { ProgramCycle } from '@api/programCycleApi';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  AllPaymentPlansForTableQuery,
  AllPaymentPlansForTableQueryVariables,
  useAllPaymentPlansForTableQuery,
} from '@generated/graphql';
import { UniversalTable } from '@containers/tables/UniversalTable';
import { headCells } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansHeadCells';
import { PaymentPlanTableRow } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlanTableRow';
import { adjustHeadCells } from '@utils/utils';
import { useProgramContext } from 'src/programContext';

interface PaymentPlansTableProps {
  programCycle: ProgramCycle;
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

  const initialVariables: AllPaymentPlansForTableQueryVariables = {
    businessArea,
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
  };

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
    <UniversalTable<
      AllPaymentPlansForTableQuery['allPaymentPlans']['edges'][0]['node'],
      AllPaymentPlansForTableQueryVariables
    >
      defaultOrderBy="-createdAt"
      title={title}
      headCells={adjustedHeadCells}
      query={useAllPaymentPlansForTableQuery}
      queriedObjectName="allPaymentPlans"
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PaymentPlanTableRow
          key={row.id}
          paymentPlan={row}
          canViewDetails={canViewDetails}
        />
      )}
    />
  );
};
