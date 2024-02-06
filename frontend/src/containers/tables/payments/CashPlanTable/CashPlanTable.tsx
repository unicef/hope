import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllCashPlansAndPaymentPlansQueryVariables,
  CashPlanAndPaymentPlanNode,
  ProgramQuery,
  useAllCashPlansAndPaymentPlansQuery,
} from '../../../../__generated__/graphql';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './CashPlanTableHeadCells';
import { CashPlanTableRow } from './CashPlanTableRow';

interface CashPlanTableProps {
  program: ProgramQuery['program'];
}

export function CashPlanTable({ program }: CashPlanTableProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const initialVariables = {
    program: program.id,
    businessArea,
    isPaymentVerificationPage: false,
  };

  return (
    <UniversalTable<
    CashPlanAndPaymentPlanNode,
    AllCashPlansAndPaymentPlansQueryVariables
    >
      title={t('Payment Plans')}
      headCells={headCells}
      query={useAllCashPlansAndPaymentPlansQuery}
      queriedObjectName="allCashPlansAndPaymentPlans"
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
