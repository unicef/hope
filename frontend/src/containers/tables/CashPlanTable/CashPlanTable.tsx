import React, { ReactElement } from 'react';
import {
  AllCashPlansQueryVariables,
  CashPlanNode,
  ProgramNode,
  useAllCashPlansQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './CashPlanTableHeadCells';
import { CashPlanTableRow } from './CashPlanTableRow';

interface CashPlanTableProps {
  program: ProgramNode;
}
export function CashPlanTable({ program }: CashPlanTableProps): ReactElement {
  const initialVariables = {
    program: program.id,
  };

  return (
    <UniversalTable<CashPlanNode, AllCashPlansQueryVariables>
      title='Cash Plans'
      headCells={headCells}
      query={useAllCashPlansQuery}
      queriedObjectName='allCashPlans'
      initialVariables={initialVariables}
      renderRow={(row) => <CashPlanTableRow key={row.id} cashPlan={row} />}
    />
  );
}
