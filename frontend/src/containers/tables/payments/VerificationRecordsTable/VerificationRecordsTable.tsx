import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentVerificationsQueryVariables,
  PaymentVerificationNode,
  useAllPaymentVerificationsQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './VerificationRecordsHeadCells';
import { VerificationRecordsTableRow } from './VerificationRecordsTableRow';

interface VerificationRecordsTableProps {
  paymentPlanId?: string;
  filter;
  canViewRecordDetails: boolean;
  businessArea: string;
}

export const VerificationRecordsTable = ({
  paymentPlanId,
  filter,
  canViewRecordDetails,
  businessArea,
}: VerificationRecordsTableProps): ReactElement => {
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
      queriedObjectName='allPaymentVerifications'
      initialVariables={initialVariables}
      renderRow={(paymentVerification) => (
        <VerificationRecordsTableRow
          key={paymentVerification.id}
          paymentVerification={paymentVerification}
          canViewRecordDetails={canViewRecordDetails}
        />
      )}
    />
  );
};
