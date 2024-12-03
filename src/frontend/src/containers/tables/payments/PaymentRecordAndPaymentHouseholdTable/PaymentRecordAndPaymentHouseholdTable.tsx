import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentRecordsAndPaymentsQueryVariables,
  HouseholdNode,
  PaymentRecordAndPaymentNode,
  useAllPaymentRecordsAndPaymentsQuery,
} from '@generated/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './PaymentRecordAndPaymentHouseholdTableHeadCells';
import { PaymentRecordAndPaymentHouseholdTableRow } from './PaymentRecordAndPaymentHouseholdTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';

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
  const { programId } = useBaseUrl();
  const initialVariables = {
    household: household?.id,
    businessArea,
    program: programId,
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
