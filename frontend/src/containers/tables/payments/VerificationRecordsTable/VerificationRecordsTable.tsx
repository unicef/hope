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

export function VerificationRecordsTable({
  id,
  filter,
  canViewRecordDetails,
  businessArea,
}): ReactElement {
  const { t } = useTranslation();

  const initialVariables: AllPaymentVerificationsQueryVariables = {
    cashPlanPaymentVerification: id,
    search: filter.search,
    status: filter.status,
    businessArea,
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
      renderRow={(row) => (
        <VerificationRecordsTableRow
          key={row.id}
          record={row}
          canViewRecordDetails={canViewRecordDetails}
        />
      )}
    />
  );
}
