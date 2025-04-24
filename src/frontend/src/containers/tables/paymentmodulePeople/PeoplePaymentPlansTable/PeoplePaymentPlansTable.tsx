import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedPaymentPlanListList } from '@restgenerated/models/PaginatedPaymentPlanListList';
import { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
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
  const initialQueryVariables = {
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
  };

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const {
    data: paymentPlansData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentPlanListList>({
    queryKey: ['businessAreasProgramsPaymentPlansList', queryVariables],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentPlansList(
        queryVariables,
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
      RestService.restBusinessAreasProgramsPaymentPlansCountRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
      }),
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
