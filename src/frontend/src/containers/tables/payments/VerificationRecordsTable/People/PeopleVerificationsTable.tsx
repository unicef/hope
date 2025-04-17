import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { PeopleVerificationRecordsTableRow } from '@containers/tables/payments/VerificationRecordsTable/People/PeopleVerificationRecordsTableRow';
import { AllPaymentVerificationsQueryVariables } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedPaymentVerificationPlanListList } from '@restgenerated/models/PaginatedPaymentVerificationPlanListList';
import { PaymentVerificationPlanList } from '@restgenerated/models/PaymentVerificationPlanList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { headCells } from './PeopleVerificationsHeadCells';

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

  const initialQueryVariables: AllPaymentVerificationsQueryVariables = {
    ...filter,
    businessArea,
    paymentPlanId,
  };

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const {
    data: paymentVerificationsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentVerificationPlanListList>({
    queryKey: [
      'businessAreasProgramsPaymentVerificationsList',
      businessArea,
      programId,
      queryVariables,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentVerificationsList({
        businessAreaSlug: businessArea,
        programSlug: programId,
      });
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
      data={paymentVerificationsData}
      renderRow={(paymentVerification: PaymentVerificationPlanList) => (
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
