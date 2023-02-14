import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentRecordsAndPaymentsQueryVariables,
  HouseholdNode,
  PaymentRecordAndPaymentNode,
  useAllPaymentRecordsAndPaymentsQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
// TODO: rename files
import { headCells } from './PaymentRecordHouseholdTableHeadCells';
import { PaymentRecordAndPaymentHouseholdTableRow } from './PaymentRecordHouseholdTableRow';

interface PaymentRecordAndPaymentTableProps {
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
}: PaymentRecordAndPaymentTableProps): ReactElement {
  const { t } = useTranslation();
  const initialVariables = {
    household: household?.id,
    businessArea,
  };
  return (
    <UniversalTable<
      PaymentRecordAndPaymentNode,
      AllPaymentRecordsAndPaymentsQueryVariables
    >
      title={t('Payment Records')}
      headCells={headCells}
      query={useAllPaymentRecordsAndPaymentsQuery}
      queriedObjectName='allPaymentRecordsAndPayments'
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PaymentRecordAndPaymentHouseholdTableRow
          key={row.id}
          paymentRecordOrPayment={row}
          openInNewTab={openInNewTab}
          canViewDetails={canViewPaymentRecordDetails}
        />
      )}
    />
  );
}
