import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { createApiParams } from '@utils/apiUtils';
import type { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';
import type { PaymentList } from '@restgenerated/models/PaymentList';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { adjustHeadCells } from '@utils/utils';
import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { useTableState } from '@hooks/useTableState';
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
  const { isSocialDctType } = useProgramContext();

  const filterVariables = useMemo(
    () => ({
      ...filter,
      businessAreaSlug: businessArea,
      programCode: programId,
      paymentVerificationPk: paymentPlanId,
    }),
    [filter, businessArea, programId, paymentPlanId],
  );

  const table = useTableState();
  const { page } = table;
  const listVariables = useMemo(
    () => ({ ...filterVariables, ...table.paginationParams }),
    [filterVariables, table.paginationParams],
  );

  // Add count query for verification records, only enabled on first page
  const verificationsCountParams = {
    businessAreaSlug: businessArea,
    programCode: programId,
    paymentVerificationPk: paymentPlanId,
    ...filterVariables,
  };
  const { data: verificationCountData } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentVerificationsVerificationsCountRetrieve,
      verificationsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsVerificationsCountRetrieve(
        verificationsCountParams,
      ),
    enabled: page === 0,
  });

  const itemsCount = usePersistedCount(page, verificationCountData);

  const verificationsListParams = createApiParams(
    {
      businessAreaSlug: businessArea,
      programCode: programId,
      paymentVerificationPk: paymentPlanId,
    },
    listVariables,
  );
  const {
    data: paymentsData,
    isLoading,
    isFetching,
    error,
  } = useQuery<PaginatedPaymentListList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentVerificationsVerificationsList,
      verificationsListParams,
    ),
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentVerificationsVerificationsList(
        verificationsListParams,
      );
    },
    placeholderData: keepPreviousData,
  });

  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const replacements = {
    payment_record__head_of_household__family_name: (_beneficiaryGroup) =>
      isSocialDctType
        ? _beneficiaryGroup?.memberLabel
        : `Head of ${_beneficiaryGroup?.groupLabel}`,
    payment_record__household__unicef_id: (_beneficiaryGroup) =>
      isSocialDctType
        ? `${_beneficiaryGroup?.memberLabel} ID`
        : `${_beneficiaryGroup?.groupLabel} ID`,
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
      isFetching={isFetching}
      error={error}
      tableState={table}
      data={paymentsData}
      itemsCount={itemsCount}
      renderRow={(payment: PaymentList) => (
        <VerificationRecordsTableRow
          key={payment.id}
          payment={payment}
          canViewRecordDetails={canViewRecordDetails}
          paymentPlanId={paymentPlanId}
          showStatusColumn={false}
        />
      )}
    />
  );
}
