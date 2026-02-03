import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { PeopleVerificationRecordsTableRow } from '@containers/tables/payments/VerificationRecordsTable/People/PeopleVerificationRecordsTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaymentList } from '@restgenerated/models/PaymentList';
import { RestService } from '@restgenerated/services/RestService';
import { createApiParams } from '@utils/apiUtils';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { usePersistedCount } from '@hooks/usePersistedCount';
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

  const [page, setPage] = useState(0);

  const initialQueryVariables = useMemo(
    () => ({
      ...filter,
      businessAreaSlug: businessArea,
      programSlug: programId,
      paymentVerificationPk: paymentPlanId,
      page,
    }),
    [filter, businessArea, programId, paymentPlanId, page],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const {
    data: paymentsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentListList>({
    queryKey: [
      'businessAreasProgramsPaymentVerificationsVerificationsList',
      queryVariables,
      businessArea,
      programId,
      paymentPlanId,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentVerificationsVerificationsList(
        createApiParams(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
            paymentVerificationPk: paymentPlanId,
          },
          queryVariables,
          { withPagination: true },
        ),
      );
    },
  });

  const { data: countData } = useQuery({
    queryKey: [
      'businessAreasProgramsPaymentVerificationsVerificationsCount',
      queryVariables,
      businessArea,
      programId,
      paymentPlanId,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentVerificationsVerificationsCountRetrieve(
        createApiParams(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
            paymentVerificationPk: paymentPlanId,
          },
          queryVariables,
        ),
      );
    },
    enabled: page === 0,
  });

  const itemsCount = usePersistedCount(page, countData);

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
          paymentPlanId={paymentPlanId}
          canViewRecordDetails={canViewRecordDetails}
          showStatusColumn={false}
        />
      )}
    />
  );
}
