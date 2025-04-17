import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentsForTableQueryVariables,
  PaymentNode,
  useAllPaymentsForTableQuery,
} from '@generated/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './PaymentsPeopleTableHeadCells';
import { PaymentsPeopleTableRow } from './PaymentsPeopleTableRow';
import { useBaseUrl } from '@hooks/useBaseUrl';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { error } from 'console';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

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

  //TODO: for specific PEOPLE
  const {
    data: paymentsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentHouseholdListList>({
    queryKey: [
      'businessAreasProgramsPaymentPlansPaymentsList',
      businessArea,
      programId,
      queryVariables,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentPlansPaymentsList({
        businessAreaSlug: businessArea,
        programSlug: programId,
        paymentPlanId: paymentPlan.id,
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
