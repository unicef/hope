import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaymentPlanTableRow } from './PaymentPlanTableRow';
import { headCells } from './PaymentPlansHeadCells';
import { useProgramContext } from 'src/programContext';
import { adjustHeadCells } from '@utils/utils';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { PaginatedPaymentPlanListList } from '@restgenerated/models/PaginatedPaymentPlanListList';
import { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';
import { CountResponse } from '@restgenerated/models/CountResponse';

interface PaymentPlansTableProps {
  filter;
  canViewDetails: boolean;
}

function PaymentPlansTable({
  filter,
  canViewDetails,
}: PaymentPlansTableProps): ReactElement {
  const { t } = useTranslation();
  const { programId, businessArea } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const initialQueryVariables = {
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
    queryKey: [
      'businessAreasProgramsPaymentPlansList',
      businessArea,
      programId,
      queryVariables,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentPlansList({
        businessAreaSlug: businessArea,
        programSlug: programId,
      });
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
        ...queryVariables,
      }),
  });

  const replacements = {
    totalHouseholdsCount: (_beneficiaryGroup) =>
      `Num. of ${_beneficiaryGroup?.groupLabelPlural}`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  return (
    <UniversalRestTable
      defaultOrderBy="-createdAt"
      title={t('Payment Plans')}
      headCells={adjustedHeadCells as any}
      data={paymentPlansData}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      itemsCount={dataPaymentPlansCount?.count}
      renderRow={(row: PaymentPlanList) => (
        <PaymentPlanTableRow
          key={row.id}
          plan={row}
          canViewDetails={canViewDetails}
        />
      )}
    />
  );
}

export default withErrorBoundary(PaymentPlansTable, 'PaymentPlansTable');
