import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentVerificationsQueryVariables,
  PaymentVerificationNode,
  useAllPaymentVerificationsQuery,
} from '@generated/graphql';
import { UniversalTable } from '../../../UniversalTable';
import { headCells } from './PeopleVerificationsHeadCells';
import { PeopleVerificationRecordsTableRow } from '@containers/tables/payments/VerificationRecordsTable/People/PeopleVerificationRecordsTableRow';

interface PeopleVerificationsTableProps {
  paymentPlanId?: string;
  filter;
  canViewRecordDetails: boolean;
  businessArea: string;
}

export function PeopleVerificationsTable({
  paymentPlanId,
  filter,
  canViewRecordDetails,
  businessArea,
}: PeopleVerificationsTableProps): ReactElement {
  const { t } = useTranslation();

  const initialVariables: AllPaymentVerificationsQueryVariables = {
    ...filter,
    businessArea,
    paymentPlanId,
  };

  return (
    <UniversalTable<
      PaymentVerificationNode,
      AllPaymentVerificationsQueryVariables
    >
      title={t('Verification Records')}
      headCells={headCells}
      query={useAllPaymentVerificationsQuery}
      queriedObjectName="allPaymentVerifications"
      initialVariables={initialVariables}
      renderRow={(paymentVerification) => (
        <PeopleVerificationRecordsTableRow
          key={paymentVerification.id}
          paymentVerification={paymentVerification}
          canViewRecordDetails={canViewRecordDetails}
          showStatusColumn={false}
        />
      )}
    />
  );
}
