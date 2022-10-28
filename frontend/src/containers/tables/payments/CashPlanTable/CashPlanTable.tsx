import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import {
  AllCashPlansAndPaymentPlansQueryVariables,
  CashPlanAndPaymentPlanNode,
  ProgramNode,
  useAllCashPlansAndPaymentPlansQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
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
    <UniversalTable<
      CashPlanAndPaymentPlanNode,
      AllCashPlansAndPaymentPlansQueryVariables
    >
      title={t('Cash Plans')}
      headCells={headCells}
      query={useAllCashPlansAndPaymentPlansQuery}
      queriedObjectName='allCashPlansAndPaymentPlans'
      initialVariables={initialVariables}
      renderRow={(cashPlanAndPaymentPlanNode) => (
        <CashPlanTableRow
          key={cashPlanAndPaymentPlanNode.id}
          cashAndPaymentPlan={cashPlanAndPaymentPlanNode}
        />
      )}
    />
  );
}
