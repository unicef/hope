import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllPaymentVerificationsQueryVariables,
  PaymentVerificationNode,
  useAllPaymentVerificationsQuery,
} from '@generated/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './VerificationRecordsHeadCells';
import { VerificationRecordsTableRow } from './VerificationRecordsTableRow';
import { useProgramContext } from 'src/programContext';
import { adjustHeadCells } from '@utils/utils';

interface VerificationRecordsTableProps {
  paymentPlanId?: string;
  filter;
  canViewRecordDetails: boolean;
  businessArea: string;
}

export function VerificationRecordsTable({
  paymentPlanId,
  filter,
  canViewRecordDetails,
  businessArea,
}: VerificationRecordsTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const replacements = {
    payment_record__head_of_household__family_name: (_beneficiaryGroup) =>
      `Head of ${_beneficiaryGroup?.groupLabel}`,
    payment_record__household__unicef_id: (_beneficiaryGroup) =>
      `${_beneficiaryGroup?.groupLabel} ID`,
    payment_record__household__status: (_beneficiaryGroup) =>
      `${_beneficiaryGroup?.groupLabel} Status`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  const initialVariables: AllPaymentVerificationsQueryVariables = {
    ...filter,
    businessArea,
    paymentPlanId,
  };

  return (
    <UniversalTable<
      PaymentVerificationNode,
      AllPaymentVerificationsQueryVariables
    >
      title={t('Verification Records')}
      headCells={adjustedHeadCells}
      query={useAllPaymentVerificationsQuery}
      queriedObjectName="allPaymentVerifications"
      initialVariables={initialVariables}
      renderRow={(paymentVerification) => (
        <VerificationRecordsTableRow
          key={paymentVerification.id}
          paymentVerification={paymentVerification}
          canViewRecordDetails={canViewRecordDetails}
        />
      )}
    />
  );
}
