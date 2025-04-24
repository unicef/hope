import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';
import { PaymentList } from '@restgenerated/models/PaymentList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import { headCells } from './PaymentsHouseholdTableHeadCells';
import { PaymentsHouseholdTableRow } from './PaymentsHouseholdTableRow';

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
    id: household?.id,
    businessAreaSlug: businessArea,
    programSlug: programId,
  };
  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const {
    data: paymentsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentListList>({
    queryKey: ['businessAreasProgramsPaymentPlansPaymentsList', queryVariables],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsHouseholdsPaymentsList(
        queryVariables,
      );
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
      renderRow={(row: PaymentList) => (
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
