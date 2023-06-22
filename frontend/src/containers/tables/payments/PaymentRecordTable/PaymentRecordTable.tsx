import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentRecordsQueryVariables,
  CashPlanNode,
  PaymentRecordNode,
  useAllPaymentRecordsQuery,
} from '../../../../__generated__/graphql';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './PaymentRecordTableHeadCells';
import { PaymentRecordTableRow } from './PaymentRecordTableRow';

interface PaymentRecordTableProps {
  cashPlan: CashPlanNode;
  openInNewTab?: boolean;
}
export function PaymentRecordTable({
  cashPlan,
  openInNewTab = false,
}: PaymentRecordTableProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const initialVariables = {
    cashPlan: cashPlan.id,
    businessArea,
    program: programId,
  };
  return (
    <UniversalTable<PaymentRecordNode, AllPaymentRecordsQueryVariables>
      title={t('Payment Records')}
      headCells={headCells}
      query={useAllPaymentRecordsQuery}
      queriedObjectName='allPaymentRecords'
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PaymentRecordTableRow
          key={row.id}
          paymentRecord={row}
          openInNewTab={openInNewTab}
        />
      )}
    />
  );
}
