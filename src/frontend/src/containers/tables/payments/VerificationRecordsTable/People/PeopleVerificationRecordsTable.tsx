import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { createApiParams } from '@utils/apiUtils';
import { PeopleVerificationRecordsTableRow } from '@containers/tables/payments/VerificationRecordsTable/People/PeopleVerificationRecordsTableRow';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { PaginatedPaymentVerificationPlanListList } from '@restgenerated/models/PaginatedPaymentVerificationPlanListList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { headCells } from './PeopleVerificationRecordsHeadCells';
import { PaymentList } from '@restgenerated/models/PaymentList';

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
  const { programId } = useBaseUrl();

  const initialQueryVariables = {
    ...filter,
    paymentPlanId,
    businessAreaSlug: businessArea,
    programSlug: programId,
  };

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const {
    data: paymentsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentVerificationPlanListList>({
    queryKey: [
      'businessAreasProgramsPaymentVerificationsList',
      queryVariables,
      businessArea,
      programId,
      paymentPlanId,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentVerificationsList(
        createApiParams(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
            paymentPlanId,
          },
          queryVariables,
          { withPagination: true },
        ),
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
        />
      )}
    />
  );
}
