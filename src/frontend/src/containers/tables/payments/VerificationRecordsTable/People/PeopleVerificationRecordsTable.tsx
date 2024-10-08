import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentVerificationsQueryVariables,
  PaymentVerificationNode,
  useAllPaymentVerificationsQuery,
} from '@generated/graphql';
import { UniversalTable } from '../../../UniversalTable';
import { headCells } from './PeopleVerificationRecordsHeadCells';
import { PeopleVerificationRecordsTableRow } from '@containers/tables/payments/VerificationRecordsTable/People/PeopleVerificationRecordsTableRow';

interface PeopleVerificationRecordsTableProps {
  paymentPlanId?: string;
  filter;
  canViewRecordDetails: boolean;
  businessArea: string;
}

export function PeopleVerificationRecordsTable({
  paymentPlanId,
  filter,
  canViewRecordDetails,
  businessArea,
}: PeopleVerificationRecordsTableProps): ReactElement {
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
        />
      )}
    />
  );
}
