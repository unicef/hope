import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
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
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const initialVariables = {
    program: program.id,
    businessArea,
  };

  return (
    <UniversalTable<CashPlanNode, AllCashPlansQueryVariables>
      title={t('Cash Plans')}
      headCells={headCells}
      query={useAllCashPlansQuery}
      queriedObjectName='allCashPlans'
      initialVariables={initialVariables}
      renderRow={(row) => <CashPlanTableRow key={row.id} cashPlan={row} />}
    />
  );
}
