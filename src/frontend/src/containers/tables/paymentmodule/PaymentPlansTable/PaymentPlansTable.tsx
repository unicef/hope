import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaymentPlanTableRow } from './PaymentPlanTableRow';
import { headCells } from './PaymentPlansHeadCells';
import { useProgramContext } from 'src/programContext';
import { adjustHeadCells } from '@utils/utils';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { createApiParams } from '@utils/apiUtils';
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

  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programSlug: programId,
      search: filter.search,
      status: filter.status,
      totalEntitledQuantityUsdFrom: filter.totalEntitledQuantityUsdFrom || null,
      totalEntitledQuantityUsdTo: filter.totalEntitledQuantityUsdTo || null,
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
      filter.totalEntitledQuantityUsdFrom,
      filter.totalEntitledQuantityUsdTo,
      filter.dispersionStartDate,
      filter.dispersionEndDate,
      filter.isFollowUp,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

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
      programId,
      businessArea,
      queryVariables,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansCountRetrieve(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
        ),
      ),
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
