import React, {ReactElement} from 'react';
import {useBusinessArea} from '../../../hooks/useBusinessArea';
import {
  AllCashPlansQueryVariables,
  CashPlanNode,
  ProgramNode,
  useAllCashPlansQuery,
} from '../../../__generated__/graphql';
import {UniversalTable} from '../UniversalTable';
import {headCells} from './CashPlanTableHeadCells';
import {CashPlanTableRow} from './CashPlanTableRow';

interface CashPlanTableProps {
  program: ProgramNode;
}
export function CashPlanTable({ program }: CashPlanTableProps): ReactElement {
  const businessArea = useBusinessArea();
  const initialVariables = {
    program: program.id,
    businessArea,
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
