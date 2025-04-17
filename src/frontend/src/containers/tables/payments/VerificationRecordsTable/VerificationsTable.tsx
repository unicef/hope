import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedPaymentVerificationPlanListList } from '@restgenerated/models/PaginatedPaymentVerificationPlanListList';
import { PaymentVerificationPlanList } from '@restgenerated/models/PaymentVerificationPlanList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import { VerificationRecordsTableRow } from './VerificationRecordsTableRow';
import { headCells } from './VerificationsHeadCells';

interface VerificationsTableProps {
  paymentPlanId?: string;
  filter;
  canViewRecordDetails: boolean;
  businessArea: string;
}

export function VerificationsTable({
  paymentPlanId,
  filter,
  canViewRecordDetails,
  businessArea,
}: VerificationsTableProps): ReactElement {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();

  const initialQueryVariables = {
    ...filter,
    businessArea,
    paymentPlanId,
  };

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  const {
    data: paymentVerificationsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentVerificationPlanListList>({
    queryKey: [
      'businessAreasProgramsPaymentVerificationsList',
      businessArea,
      programId,
      queryVariables,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentVerificationsList({
        businessAreaSlug: businessArea,
        programSlug: programId,
      });
    },
  });

  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const replacements = {
    payment_record__head_of_household__family_name: (_beneficiaryGroup) =>
      `Head of ${_beneficiaryGroup?.groupLabel}`,
    payment_record__household__unicef_id: (_beneficiaryGroup) =>
      `${_beneficiaryGroup?.groupLabel} ID`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  return (
    <UniversalRestTable
      title={t('Verification Records')}
      headCells={adjustedHeadCells}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      data={paymentVerificationsData}
      renderRow={(paymentVerification: PaymentVerificationPlanList) => (
        <VerificationRecordsTableRow
          key={paymentVerification.id}
          paymentVerification={paymentVerification}
          canViewRecordDetails={canViewRecordDetails}
          showStatusColumn={false}
        />
      )}
    />
  );
}
