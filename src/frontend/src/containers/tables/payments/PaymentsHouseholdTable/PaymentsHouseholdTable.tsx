import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentsForTableQueryVariables,
  PaymentNode,
  useAllPaymentsForTableQuery,
} from '@generated/graphql';
import { UniversalTable } from '../../UniversalTable';
import { PaymentsHouseholdTableRow } from './PaymentsHouseholdTableRow';
import { adjustHeadCells } from '@utils/utils';
import { useProgramContext } from 'src/programContext';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { headCells } from './PaymentsHouseholdTableHeadCells';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';

interface PaymentsHouseholdTableProps {
  household?: HouseholdDetail;
  openInNewTab?: boolean;
  businessArea: string;
  canViewPaymentRecordDetails: boolean;
}
function PaymentsHouseholdTable({
  household,
  openInNewTab = false,
  businessArea,
  canViewPaymentRecordDetails,
}: PaymentsHouseholdTableProps): ReactElement {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();
  const initialQueryVariables = {
    householdId: household?.id,
    businessArea,
    program: programId,
  };
  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  //TODO: for specific household
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
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const replacements = {
    headOfHousehold: (_beneficiaryGroup) =>
      `Head of ${_beneficiaryGroup?.groupLabel}`,
    fullName: (_beneficiaryGroup) => `${_beneficiaryGroup?.memberLabel}`,
    relationship: (_beneficiaryGroup) =>
      `Relationship to Head of ${_beneficiaryGroup?.groupLabel}`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  return (
    <UniversalRestTable
      title={t('Payments')}
      headCells={adjustedHeadCells}
      data={paymentsData}
      error={error}
      isLoading={isLoading}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      renderRow={(row: PaymentHousehold) => (
        <PaymentsHouseholdTableRow
          key={row.id}
          payment={row}
          openInNewTab={openInNewTab}
          canViewDetails={canViewPaymentRecordDetails}
        />
      )}
    />
  );
}
export default withErrorBoundary(
  PaymentsHouseholdTable,
  'PaymentsHouseholdTable',
);
