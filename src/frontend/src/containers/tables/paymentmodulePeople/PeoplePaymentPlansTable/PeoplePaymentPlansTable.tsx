import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedPaymentPlanListList } from '@restgenerated/models/PaginatedPaymentPlanListList';
import { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { createApiParams } from '@utils/apiUtils';
import { PeoplePaymentPlanTableRow } from './PeoplePaymentPlanTableRow';
import { headCells } from './PeoplePaymentPlansHeadCells';
import { CountResponse } from '@restgenerated/models/CountResponse';

interface PeoplePaymentPlansTableProps {
  filter;
  canViewDetails: boolean;
}

export const PeoplePaymentPlansTable = ({
  filter,
  canViewDetails,
}: PeoplePaymentPlansTableProps): ReactElement => {
  const { t } = useTranslation();
  const { programId, businessArea } = useBaseUrl();

  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programSlug: programId,
      search: filter.search,
      status: filter.status,
      totalEntitledQuantityFrom: filter.totalEntitledQuantityFrom || null,
      totalEntitledQuantityTo: filter.totalEntitledQuantityTo || null,
      dispersionStartDate: filter.dispersionStartDate || null,
      dispersionEndDate: filter.dispersionEndDate || null,
      isFollowUp: filter.isFollowUp ? true : null,
      isPaymentPlan: true,
    }),
    [
      businessArea,
      programId,
      filter.search,
      filter.status,
      filter.totalEntitledQuantityFrom,
      filter.totalEntitledQuantityTo,
      filter.dispersionStartDate,
      filter.dispersionEndDate,
      filter.isFollowUp,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const [page, setPage] = useState(0);

  const {
    data: paymentPlansData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentPlanListList>({
    queryKey: [
      'businessAreasProgramsPaymentPlansList',
      queryVariables,
      businessArea,
      programId,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentPlansList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
          { withPagination: true },
        ),
      );
    },
  });

  const { data: dataPaymentPlansCount } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsPaymentPlansCountRetrieve',
      queryVariables,
      programId,
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansCountRetrieve(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
        ),
      ),
    enabled: !!businessArea && !!programId && page === 0,
  });

  return (
    <UniversalRestTable
      defaultOrderBy="-createdAt"
      title={t('Payment Plans')}
      headCells={headCells}
      data={paymentPlansData}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      itemsCount={dataPaymentPlansCount?.count}
      page={page}
      setPage={setPage}
      renderRow={(row: PaymentPlanList) => (
        <PeoplePaymentPlanTableRow
          key={row.id}
          plan={row}
          canViewDetails={canViewDetails}
        />
      )}
    />
  );
};

export default withErrorBoundary(
  PeoplePaymentPlansTable,
  'PeoplePaymentPlansTable',
);
