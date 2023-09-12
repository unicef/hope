import React, { ReactElement } from 'react';
import {
  AllPaymentPlansForTableQueryVariables,
  PaymentPlanNode,
  useAllPaymentPlansForTableQuery,
} from '../../../../../__generated__/graphql';
import { useBaseUrl } from '../../../../../hooks/useBaseUrl';
import { UniversalTable } from '../../../UniversalTable';
import { headCells } from './PaymentPlansHeadCellsProgramCycle';
import { PaymentPlanTableRowProgramCycle } from './PaymentPlanTableRowProgramCycle';

interface PaymentPlansTableProgramCycleProps {
  filter;
  canViewDetails: boolean;
  title?: string;
}

export const PaymentPlansTableProgramCycle = ({
  filter,
  canViewDetails,
  title = 'Payment Plans',
}: PaymentPlansTableProgramCycleProps): ReactElement => {
  const { programId, businessArea } = useBaseUrl();
  const initialVariables: AllPaymentPlansForTableQueryVariables = {
    businessArea,
    search: filter.search,
    status: filter.status,
    totalEntitledQuantityFrom: filter.totalEntitledQuantityFrom,
    totalEntitledQuantityTo: filter.totalEntitledQuantityTo,
    dispersionStartDate: filter.dispersionStartDate,
    dispersionEndDate: filter.dispersionEndDate,
    isFollowUp: filter.isFollowUp ? true : null,
    program: programId,
  };

  return (
    <UniversalTable<PaymentPlanNode, AllPaymentPlansForTableQueryVariables>
      defaultOrderBy='-createdAt'
      title={title}
      headCells={headCells}
      query={useAllPaymentPlansForTableQuery}
      queriedObjectName='allPaymentPlans'
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PaymentPlanTableRowProgramCycle
          key={row.id}
          plan={row}
          canViewDetails={canViewDetails}
        />
      )}
    />
  );
};
