import React, { ReactElement } from 'react';
import {
  AllPaymentPlansForTableQueryVariables,
  PaymentPlanNode,
  useAllPaymentPlansForTableQuery,
} from '../../../../__generated__/graphql';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { UniversalTable } from '../../UniversalTable';
import { FollowUpPaymentPlanTableRow } from './FollowUpPaymentPlanTableRow';
import { headCells } from './FollowUpPaymentPlansHeadCells';

interface FollowUpPaymentPlansTableProps {
  filter;
  canViewDetails: boolean;
  title?: string;
}

export const FollowUpPaymentPlansTable = ({
  filter,
  canViewDetails,
  title = 'Payment Plans',
}: FollowUpPaymentPlansTableProps): ReactElement => {
  const { programId, businessArea } = useBaseUrl();
  const initialVariables: AllPaymentPlansForTableQueryVariables = {
    businessArea,
    search: filter.search,
    status: filter.status,
    totalEntitledQuantityFrom: filter.totalEntitledQuantityFrom,
    totalEntitledQuantityTo: filter.totalEntitledQuantityTo,
    dispersionStartDate: filter.dispersionStartDate,
    dispersionEndDate: filter.dispersionEndDate,
    isFollowUp: true,
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
        <FollowUpPaymentPlanTableRow
          key={row.id}
          plan={row}
          canViewDetails={canViewDetails}
        />
      )}
    />
  );
};
