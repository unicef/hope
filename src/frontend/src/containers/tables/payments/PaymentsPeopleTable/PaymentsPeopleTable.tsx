import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { headCells } from './PaymentsPeopleTableHeadCells';
import { PaymentsPeopleTableRow } from './PaymentsPeopleTableRow';
import { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';
import { createApiParams } from '@utils/apiUtils';

interface PaymentsPeopleTableProps {
  household?: HouseholdDetail;
  openInNewTab?: boolean;
  businessArea: string;
  canViewPaymentRecordDetails: boolean;
}
function PaymentsPeopleTable({
  household,
  openInNewTab = false,
  businessArea,
  canViewPaymentRecordDetails,
}: PaymentsPeopleTableProps): ReactElement {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();

  const initialQueryVariables = {
    businessAreaSlug: businessArea,
    programSlug: programId,
    id: household.id,
  };
  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  const [page, setPage] = useState(0);

  // Add count query for payments, only enabled on first page
  const { data: paymentsCountData } = useQuery({
    queryKey: [
      'businessAreasProgramsPaymentPlansPaymentsCount',
      queryVariables,
      businessArea,
      household.id,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsCountRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
        paymentPlanPk: household.id,
        ...queryVariables,
      }),
    enabled: page === 0,
  });

  const {
    data: paymentsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentListList>({
    queryKey: [
      'businessAreasProgramsPaymentPlansPaymentsList',
      queryVariables,
      businessArea,
      household.id,
      programId,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsHouseholdsPaymentsList(
        createApiParams(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
            id: household.id,
          },
          queryVariables,
          { withPagination: true },
        ),
      );
    },
  });

  return (
    <UniversalRestTable
      title={t('Payment Records')}
      headCells={headCells}
      data={paymentsData}
      error={error}
      isLoading={isLoading}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      page={page}
      setPage={setPage}
      itemsCount={paymentsCountData?.count}
      renderRow={(row) => (
        <PaymentsPeopleTableRow
          key={row.id}
          payment={row}
          openInNewTab={openInNewTab}
          canViewDetails={canViewPaymentRecordDetails}
        />
      )}
    />
  );
}

export default withErrorBoundary(PaymentsPeopleTable, 'PaymentsPeopleTable');
