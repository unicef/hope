import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentsForTableQueryVariables,
  HouseholdNode,
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

interface PaymentsHouseholdTableProps {
  household?: HouseholdNode;
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
  const initialVariables = {
    householdId: household?.id,
    businessArea,
    program: programId,
  };
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
    <UniversalTable<PaymentNode, AllPaymentsForTableQueryVariables>
      title={t('Payments')}
      headCells={adjustedHeadCells}
      query={useAllPaymentsForTableQuery}
      queriedObjectName="allPayments"
      initialVariables={initialVariables}
      renderRow={(row) => (
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
