import React from 'react';
import { ProgramCycle } from '@api/programCycleApi';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  AllPaymentPlansForTableQuery,
  AllPaymentPlansForTableQueryVariables,
  PaymentPlanNode,
  useAllPaymentPlansForTableQuery,
} from '@generated/graphql';
import { UniversalTable } from '@containers/tables/UniversalTable';
import { headCells } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlansHeadCells';
import { PaymentPlanTableRow } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/PaymentPlanTableRow';

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
}: PaymentPlansTableProps): React.ReactElement => {
  const { programId, businessArea } = useBaseUrl();
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
  };

  return (
    <UniversalTable<
      AllPaymentPlansForTableQuery['allPaymentPlans']['edges'][0]['node'],
      AllPaymentPlansForTableQueryVariables
    >
      defaultOrderBy="-createdAt"
      title={title}
      headCells={headCells}
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
