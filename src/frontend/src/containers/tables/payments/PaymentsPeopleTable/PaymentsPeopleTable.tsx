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
    householdId: household?.id,
    businessArea,
    program: programId,
  };
  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const {
    data: paymentsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentListList>({
    queryKey: [
      'businessAreasProgramsPaymentPlansPaymentsList',
      businessArea,
      programId,
      queryVariables,
      household.id,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsHouseholdsPaymentsList({
        businessAreaSlug: businessArea,
        programSlug: programId,
        id: household.id,
        ...queryVariables,
      });
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
