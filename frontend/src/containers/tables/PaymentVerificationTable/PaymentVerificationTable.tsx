import React, { ReactElement } from 'react';
import styled from 'styled-components';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './PaymentVerificationHeadCells';
import { PaymentVerificationTableRow } from './PaymentVerificationTableRow';
import {
  AllCashPlansQueryVariables,
  CashPlanNode,
  ProgramNode,
  useAllCashPlansQuery,
} from '../../../__generated__/graphql';

interface PaymentVerificationTableProps {
  program: ProgramNode;
}
export function PaymentVerificationTable({
  program,
}: PaymentVerificationTableProps): ReactElement {
  // const initialVariables = {
  //   program: program.id,
  // };

  return (
    <UniversalTable<CashPlanNode, AllCashPlansQueryVariables>
      title='List Of Cash Plans'
      headCells={headCells}
      query={useAllCashPlansQuery}
      queriedObjectName='allCashPlans'
      initialVariables={null}
      renderRow={(row) => (
        <PaymentVerificationTableRow key={row.id} plan={row} />
      )}
    />
  );
}
