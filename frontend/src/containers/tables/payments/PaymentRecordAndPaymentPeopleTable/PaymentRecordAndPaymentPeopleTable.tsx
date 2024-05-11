import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentRecordsAndPaymentsQueryVariables,
  HouseholdNode,
  PaymentRecordAndPaymentNode,
  useAllPaymentRecordsAndPaymentsQuery,
} from '@generated/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './PaymentRecordAndPaymentPeopleTableHeadCells';
import { PaymentRecordAndPaymentPeopleTableRow } from './PaymentRecordAndPaymentPeopleTableRow';

interface PaymentRecordHouseholdTableProps {
  household?: HouseholdNode;
  openInNewTab?: boolean;
  businessArea: string;
  canViewPaymentRecordDetails: boolean;
}
export function PaymentRecordAndPaymentPeopleTable({
  household,
  openInNewTab = false,
  businessArea,
  canViewPaymentRecordDetails,
}: PaymentRecordHouseholdTableProps): ReactElement {
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
      queriedObjectName="allPaymentRecordsAndPayments"
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PaymentRecordAndPaymentPeopleTableRow
          key={row.id}
          paymentRecordOrPayment={row}
          openInNewTab={openInNewTab}
          canViewDetails={canViewPaymentRecordDetails}
        />
      )}
    />
  );
}
