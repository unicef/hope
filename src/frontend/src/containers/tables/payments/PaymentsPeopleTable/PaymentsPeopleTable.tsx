import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentsForTableQueryVariables,
  HouseholdNode,
  PaymentNode,
  useAllPaymentsForTableQuery,
} from '@generated/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './PaymentsPeopleTableHeadCells';
import { PaymentsPeopleTableRow } from './PaymentsPeopleTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface PaymentsPeopleTableProps {
  household?: HouseholdNode;
  openInNewTab?: boolean;
  businessArea: string;
  canViewPaymentRecordDetails: boolean;
}
function PaymentsPeopleTable({
  household,
  openInNewTab = false,
  businessArea,
  canViewPaymentRecordDetails,
}: PaymentsPeopleTableProps): ReactElement {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();

  const initialVariables = {
    householdId: household?.id,
    businessArea,
    program: programId,
  };

  return (
    <UniversalTable<PaymentNode, AllPaymentsForTableQueryVariables>
      title={t('Payment Records')}
      headCells={headCells}
      query={useAllPaymentsForTableQuery}
      queriedObjectName="allPayments"
      initialVariables={initialVariables}
      renderRow={(row) => (
        <PaymentsPeopleTableRow
          key={row.id}
          payment={row}
          openInNewTab={openInNewTab}
          canViewDetails={canViewPaymentRecordDetails}
        />
      )}
    />
  );
}

export default withErrorBoundary(PaymentsPeopleTable, 'PaymentsPeopleTable');
