import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentRecordsQueryVariables,
  HouseholdNode,
  PaymentRecordNode,
  useAllPaymentRecordsQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './PaymentRecordHouseholdTableHeadCells';
import { PaymentRecordHouseholdTableRow } from './PaymentRecordHouseholdTableRow';

interface PaymentRecordTableProps {
  household?: HouseholdNode;
  openInNewTab?: boolean;
  businessArea: string;
  canViewPaymentRecordDetails: boolean;
}
export function PaymentRecordHouseholdTable({
  household,
  openInNewTab = false,
  businessArea,
  canViewPaymentRecordDetails,
}: PaymentRecordTableProps): ReactElement {
  const { t } = useTranslation();
  const initialVariables = {
    household: household?.id,
    businessArea,
  };
  return (
    <UniversalTable<PaymentRecordNode, AllPaymentRecordsQueryVariables>
      title={t('Payment Records')}
      headCells={headCells}
      query={useAllPaymentRecordsQuery}
      queriedObjectName='allPaymentRecords'
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PaymentRecordHouseholdTableRow
          key={row.id}
          paymentRecord={row}
          openInNewTab={openInNewTab}
          canViewDetails={canViewPaymentRecordDetails}
        />
      )}
    />
  );
}
