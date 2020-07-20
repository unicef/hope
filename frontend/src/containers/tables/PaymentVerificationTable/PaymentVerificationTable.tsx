import React, { ReactElement } from 'react';
import styled from 'styled-components';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './PaymentVerificationHeadCells';
import { PaymentVerificationTableRow } from './PaymentVerificationTableRow';
import {
  AllCashPlansQueryVariables,
  CashPlanNode,
  useAllCashPlansQuery,
} from '../../../__generated__/graphql';

interface PaymentVerificationTableProps {
  filter;
}
export function PaymentVerificationTable({
  filter,
}: PaymentVerificationTableProps): ReactElement {
  const initialVariables: AllCashPlansQueryVariables = {
    program: filter.program,
    search: filter.search,
    assistanceThrough: filter.assistanceThrough,
    deliveryType: filter.deliveryType,
    verificationStatus: filter.verificationStatus,
    startDateGte: filter.startDate,
    endDateLte: filter.endDate
  };
  return (
    <UniversalTable<CashPlanNode, AllCashPlansQueryVariables>
      title='List Of Cash Plans'
      headCells={headCells}
      query={useAllCashPlansQuery}
      queriedObjectName='allCashPlans'
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PaymentVerificationTableRow key={row.id} plan={row} />
      )}
    />
  );
}
