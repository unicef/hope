import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { PeopleVerificationRecordsTableRow } from '@containers/tables/payments/VerificationRecordsTable/People/PeopleVerificationRecordsTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaymentList } from '@restgenerated/models/PaymentList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { headCells } from './PeopleVerificationsHeadCells';
import { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';

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
  const { programId } = useBaseUrl();

  const initialQueryVariables = {
    ...filter,
    businessAreaSlug: businessArea,
    programSlug: programId,
    paymentVerificationPk: paymentPlanId,
  };

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const {
    data: paymentsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentListList>({
    queryKey: [
      'businessAreasProgramsPaymentVerificationsVerificationsList',
      queryVariables,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentVerificationsVerificationsList(
        queryVariables,
      );
    },
  });

  return (
    <UniversalRestTable
      title={t('Verification Records')}
      headCells={headCells}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      data={paymentsData}
      renderRow={(payment: PaymentList) => (
        <PeopleVerificationRecordsTableRow
          key={payment.id}
          payment={payment}
          canViewRecordDetails={canViewRecordDetails}
          showStatusColumn={false}
        />
      )}
    />
  );
}
