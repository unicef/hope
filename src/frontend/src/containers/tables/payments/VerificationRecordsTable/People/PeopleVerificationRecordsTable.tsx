import { ReactElement, useEffect, useMemo, useState } from 'react';
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
  // ...existing code...
  paymentPlanId,
  filter,
  canViewRecordDetails,
  businessArea,
}: PeopleVerificationRecordsTableProps): ReactElement {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();

  const initialQueryVariables = useMemo(
    () => ({
      ...filter,
      paymentPlanId,
      businessAreaSlug: businessArea,
      programSlug: programId,
    }),
    [filter, paymentPlanId, businessArea, programId],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  const [page, setPage] = useState(0);

  // Add count query for verification records, only enabled on first page
  const { data: verificationCountData } = useQuery({
    queryKey: [
      'businessAreasProgramsPaymentVerificationsCount',
      queryVariables,
      businessArea,
      programId,
      paymentPlanId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsCountRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
        paymentPlanId,
        ...queryVariables,
      }),
    enabled: page === 0,
  });

  // Persist count after fetching on page 0
  const [persistedCount, setPersistedCount] = useState<number | undefined>(
    undefined,
  );
  useEffect(() => {
    if (page === 0 && typeof verificationCountData?.count === 'number') {
      setPersistedCount(verificationCountData.count);
    }
  }, [page, verificationCountData]);

  const itemsCount = persistedCount;
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

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
      page={page}
      setPage={setPage}
      itemsCount={itemsCount}
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
