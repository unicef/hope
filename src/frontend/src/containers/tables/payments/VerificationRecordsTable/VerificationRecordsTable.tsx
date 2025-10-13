import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';
import { PaymentList } from '@restgenerated/models/PaymentList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { adjustHeadCells } from '@utils/utils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import { headCells } from './VerificationRecordsHeadCells';
import { VerificationRecordsTableRow } from './VerificationRecordsTableRow';

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
  const { programId } = useBaseUrl();

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

  const initialQueryVariables = useMemo(
    () => ({
      ...filter,
      businessAreaSlug: businessArea,
      programSlug: programId,
      paymentVerificationPk: paymentPlanId,
    }),
    [filter, businessArea, programId, paymentPlanId],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const [page, setPage] = useState(0);

  // Add count query for verification records, only enabled on first page
  const { data: verificationCountData } = useQuery({
    queryKey: [
      'businessAreasProgramsPaymentVerificationsVerificationsCount',
      queryVariables,
      businessArea,
      programId,
      paymentPlanId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsVerificationsCountRetrieve(
        {
          businessAreaSlug: businessArea,
          programSlug: programId,
          paymentVerificationPk: paymentPlanId,
          ...queryVariables,
        },
      ),
    enabled: page === 0,
  });

  const {
    data: paymentsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentListList>({
    queryKey: [
      'businessAreasProgramsPaymentVerificationsVerificationsList',
      queryVariables,
      businessArea,
      programId,
      paymentPlanId,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentVerificationsVerificationsList(
        createApiParams(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
            paymentVerificationPk: paymentPlanId,
          },
          queryVariables,
          { withPagination: true },
        ),
      );
    },
  });

  return (
    <UniversalRestTable
      title={t('Verification Records')}
      headCells={adjustedHeadCells}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      data={paymentsData}
      page={page}
      setPage={setPage}
      itemsCount={verificationCountData?.count}
      renderRow={(payment: PaymentList) => (
        <VerificationRecordsTableRow
          key={payment.id}
          payment={payment}
          canViewRecordDetails={canViewRecordDetails}
        />
      )}
    />
  );
}
