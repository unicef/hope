import { TableWrapper } from '@components/core/TableWrapper';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box, Paper, Typography } from '@mui/material';
import { createApiParams } from '@utils/apiUtils';
import type { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { useTableState } from '@hooks/useTableState';
import { adjustHeadCells, getFilterFromQueryParams } from '@utils/utils';
import type { ReactElement } from 'react';
import { useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { headCells, headCellsPeople } from './PaymentsTableHeadCells';
import { PaymentsTableRow } from './PaymentsTableRow';
import { WarningTooltipTable } from './WarningTooltipTable';
import { PaymentsFilters } from './PaymentsFilters';
import type { PaymentList } from '@restgenerated/models/PaymentList';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';
import { useLocation } from 'react-router-dom';

const StyledBox = styled(Box)`
  background-color: #fff;
`;
interface PaymentsTableProps {
  businessArea: string;
  paymentPlan: PaymentPlanDetail;
  permissions: string[];
  canViewDetails?: boolean;
}

const PaymentsTable = ({
  businessArea,
  paymentPlan,
  permissions,
  canViewDetails = false,
}: PaymentsTableProps): ReactElement => {
  const { baseUrl, programId } = useBaseUrl();
  const { t } = useTranslation();
  const { selectedProgram, isSocialDctType } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const initialFilter = {
    householdUnicefId: '',
    individualUnicefId: '',
    collectorFullName: '',
    paymentUnicefId: '',
  };

  const [dialogPayment, setDialogPayment] = useState<PaymentList | null>(null);
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [shouldScroll, setShouldScroll] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);
  useScrollToRefOnChange(tableRef, shouldScroll, appliedFilter, () =>
    setShouldScroll(false),
  );

  const filterVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programCode: programId,
      householdUnicefId: appliedFilter.householdUnicefId || null,
      individualUnicefId: appliedFilter.individualUnicefId || null,
      collectorFullName: appliedFilter.collectorFullName || null,
      paymentUnicefId: appliedFilter.paymentUnicefId || null,
    }),
    [
      businessArea,
      programId,
      appliedFilter.householdUnicefId,
      appliedFilter.individualUnicefId,
      appliedFilter.collectorFullName,
      appliedFilter.paymentUnicefId,
    ],
  );

  const table = useTableState({
    rowsPerPageOptions: [10, 25, 50],
    defaultOrderBy: 'createdAt',
    defaultOrderDirection: 'desc',
  });
  const { page, setPage } = table;
  const listVariables = useMemo(
    () => ({ ...filterVariables, ...table.paginationParams }),
    [filterVariables, table.paginationParams],
  );

  const paymentsListParams = createApiParams(
    {
      businessAreaSlug: businessArea,
      programCode: programId,
      paymentPlanPk: paymentPlan.id,
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
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsList,
      paymentsListParams,
    ),
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentPlansPaymentsList(
        paymentsListParams,
      );
    },
    placeholderData: keepPreviousData,
  });

  // Payments count
  const paymentsCountParams = createApiParams(
    {
      businessAreaSlug: businessArea,
      programCode: programId,
      paymentPlanPk: paymentPlan.id,
    },
    filterVariables,
  );
  const { data: paymentsCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsCountRetrieve,
      paymentsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsCountRetrieve(
        paymentsCountParams,
      ),
    // fetch count only on the first page and persist it across pages
    enabled: !!businessArea && !!paymentPlan?.id && page === 0,
  });

  const itemsCount = usePersistedCount(page, paymentsCount);

  const replacements = isSocialDctType
    ? {
        individual__unicef_id: (_beneficiaryGroup) =>
          `${_beneficiaryGroup?.memberLabel} ${t('ID')}`,
        household__size: (_beneficiaryGroup) =>
          `${_beneficiaryGroup?.groupLabel} ${t('Size')}`,
      }
    : {
        household__unicef_id: (_beneficiaryGroup) =>
          `${_beneficiaryGroup?.groupLabel} ${t('ID')}`,
        household__size: (_beneficiaryGroup) =>
          `${_beneficiaryGroup?.groupLabel} ${t('Size')}`,
      };

  const adjustedHeadCells = adjustHeadCells(
    isSocialDctType ? headCellsPeople : headCells,
    beneficiaryGroup,
    replacements,
  );

  const handleAppliedFilterChange = (newFilter) => {
    setAppliedFilter(newFilter);
    setShouldScroll(true);
    setPage(0);
  };

  return (
    <>
      <Box
        sx={{
          p: 4,
        }}
      >
        <PaymentsFilters
          filter={filter}
          setFilter={setFilter}
          initialFilter={initialFilter}
          appliedFilter={appliedFilter}
          setAppliedFilter={handleAppliedFilterChange}
        />
      </Box>
      <div ref={tableRef}>
        <TableWrapper>
          <Paper>
            <StyledBox
              sx={{
                p: 6,
                display: 'flex',
                justifyContent: 'space-between',
              }}
            >
              <Typography data-cy="table-title" variant="h6">
                {t('Payee List')}
              </Typography>
            </StyledBox>
            <UniversalRestTable
              isOnPaper={false}
              headCells={adjustedHeadCells}
              tableState={table}
              isLoading={isLoading}
              isFetching={isFetching}
              error={error}
              data={paymentsData}
              itemsCount={itemsCount}
              renderRow={(row: PaymentList) => (
                <PaymentsTableRow
                  key={row.id}
                  payment={row}
                  canViewDetails={canViewDetails}
                  onWarningClick={(payment) => {
                    setDialogPayment(payment);
                  }}
                  permissions={permissions}
                />
              )}
            />
          </Paper>
        </TableWrapper>
      </div>
      <WarningTooltipTable
        paymentPlan={paymentPlan}
        payment={dialogPayment}
        setDialogOpen={() => setDialogPayment(null)}
        canViewDetails={canViewDetails}
        baseUrl={baseUrl}
      />
    </>
  );
};

export default withErrorBoundary(PaymentsTable, 'PaymentsTable');
