import type { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { TableWrapper } from '@components/core/TableWrapper';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';
import { useTableState } from '@hooks/useTableState';
import { Box, Paper, Typography } from '@mui/material';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import type { NotEligiblePaymentList } from '@restgenerated/models/NotEligiblePaymentList';
import type { PaginatedNotEligiblePaymentListList } from '@restgenerated/models/PaginatedNotEligiblePaymentListList';
import type { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';
import type { PaymentList } from '@restgenerated/models/PaymentList';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import type { Profile } from '@restgenerated/models/Profile';
import { RestService } from '@restgenerated/services/RestService';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { restQueryKey } from '@utils/queryKeys';
import { adjustHeadCells, getFilterFromQueryParams } from '@utils/utils';
import type { ReactElement } from 'react';
import { useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import type { PaymentFilterKeys } from './PaymentsFilters';
import { PaymentsFilters } from './PaymentsFilters';
import { PaymentsTableRow } from './PaymentsTableRow';
import { headCells, headCellsPeople } from './PaymentsTableHeadCells';
import { WarningTooltipTable } from './WarningTooltipTable';

const StyledBox = styled(Box)`
  background-color: #fff;
`;

const eligibleFilterKeys: PaymentFilterKeys = {
  paymentUnicefId: 'paymentUnicefId',
  individualUnicefId: 'individualUnicefId',
  householdUnicefId: 'householdUnicefId',
  collectorFullName: 'collectorFullName',
  status: 'status',
};

const notEligibleFilterKeys: PaymentFilterKeys = {
  paymentUnicefId: 'notEligiblePaymentUnicefId',
  individualUnicefId: 'notEligibleIndividualUnicefId',
  householdUnicefId: 'notEligibleHouseholdUnicefId',
  collectorFullName: 'notEligibleCollectorFullName',
  ineligibilityCause: 'notEligibleIneligibilityCause',
};

const eligibleInitialFilter = {
  paymentUnicefId: '',
  individualUnicefId: '',
  householdUnicefId: '',
  collectorFullName: '',
  status: '',
};

const notEligibleInitialFilter = {
  notEligiblePaymentUnicefId: '',
  notEligibleIndividualUnicefId: '',
  notEligibleHouseholdUnicefId: '',
  notEligibleCollectorFullName: '',
  notEligibleIneligibilityCause: [],
};

interface PaymentsTableProps {
  businessArea: string;
  paymentPlan: PaymentPlanDetail;
  permissions: string[];
  canViewDetails?: boolean;
}

interface PaymentsTableSectionProps extends PaymentsTableProps {
  notEligible?: boolean;
}

const ineligibilityCauseHeadCell: HeadCell<PaymentList> = {
  disablePadding: false,
  label: 'Ineligibility Cause',
  id: 'ineligibility_cause',
  numeric: false,
  disableSort: true,
};

const notEligibleHiddenColumns = [
  'household__size',
  'household__admin2__name',
  'financial_service_provider__name',
  'delivered_quantity',
  'fsp_auth_code',
  'reconciliation_rank',
];

const PaymentsTableSection = ({
  businessArea,
  paymentPlan,
  permissions,
  canViewDetails = false,
  notEligible = false,
}: PaymentsTableSectionProps): ReactElement => {
  const { baseUrl, programId } = useBaseUrl();
  const { t } = useTranslation();
  const { selectedProgram, isSocialDctType } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const location = useLocation();
  const filterKeys = notEligible ? notEligibleFilterKeys : eligibleFilterKeys;
  const initialFilter = notEligible
    ? notEligibleInitialFilter
    : eligibleInitialFilter;

  const [dialogPayment, setDialogPayment] = useState<PaymentList | null>(null);
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
      householdUnicefId: appliedFilter[filterKeys.householdUnicefId] || null,
      individualUnicefId: appliedFilter[filterKeys.individualUnicefId] || null,
      collectorFullName: appliedFilter[filterKeys.collectorFullName] || null,
      paymentUnicefId: appliedFilter[filterKeys.paymentUnicefId] || null,
      status:
        !notEligible && filterKeys.status
          ? appliedFilter[filterKeys.status] || null
          : null,
      ineligibilityCause:
        notEligible && filterKeys.ineligibilityCause
          ? appliedFilter[filterKeys.ineligibilityCause] || null
          : null,
    }),
    [appliedFilter, businessArea, filterKeys, notEligible, programId],
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

  const primaryParams = {
    businessAreaSlug: businessArea,
    programCode: programId,
    paymentPlanPk: paymentPlan.id,
  };
  const paymentsListParams = createApiParams(primaryParams, listVariables);
  const listService = notEligible
    ? RestService.restBusinessAreasProgramsPaymentPlansPaymentsNotEligibleList
    : RestService.restBusinessAreasProgramsPaymentPlansPaymentsList;
  const {
    data: paymentsData,
    isLoading,
    isFetching,
    error,
  } = useQuery<PaginatedPaymentListList | PaginatedNotEligiblePaymentListList>({
    queryKey: restQueryKey(listService, paymentsListParams),
    queryFn: () => listService(paymentsListParams),
    placeholderData: keepPreviousData,
  });

  const paymentsCountParams = createApiParams(primaryParams, filterVariables);
  const countService = notEligible
    ? RestService.restBusinessAreasProgramsPaymentPlansPaymentsNotEligibleCountRetrieve
    : RestService.restBusinessAreasProgramsPaymentPlansPaymentsCountRetrieve;
  const { data: paymentsCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(countService, paymentsCountParams),
    queryFn: () => countService(paymentsCountParams),
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
  const tableHeadCells = notEligible
    ? adjustedHeadCells
        .filter((headCell) => !notEligibleHiddenColumns.includes(headCell.id))
        .flatMap((headCell) =>
          headCell.id === 'status'
            ? [headCell, ineligibilityCauseHeadCell]
            : [headCell],
        )
    : adjustedHeadCells;

  const handleAppliedFilterChange = (newFilter): void => {
    setAppliedFilter(newFilter);
    setShouldScroll(true);
    setPage(0);
  };

  return (
    <>
      <Box sx={{ p: 4 }}>
        <PaymentsFilters
          filter={filter}
          setFilter={setFilter}
          initialFilter={initialFilter}
          appliedFilter={appliedFilter}
          setAppliedFilter={handleAppliedFilterChange}
          filterKeys={filterKeys}
          showStatus={!notEligible}
          showIneligibilityCause={notEligible}
        />
      </Box>
      <div
        ref={tableRef}
        data-cy={
          notEligible
            ? 'not-eligible-payments-table'
            : 'eligible-payments-table'
        }
      >
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
                {t(notEligible ? 'Not Eligible Payee List' : 'Payee List')}
              </Typography>
            </StyledBox>
            <UniversalRestTable
              isOnPaper={false}
              headCells={tableHeadCells}
              tableState={table}
              isLoading={isLoading}
              isFetching={isFetching}
              error={error}
              data={paymentsData}
              itemsCount={itemsCount}
              renderRow={(row: PaymentList | NotEligiblePaymentList) => (
                <PaymentsTableRow
                  key={row.id}
                  payment={row}
                  canViewDetails={canViewDetails}
                  onWarningClick={(payment) => setDialogPayment(payment)}
                  permissions={permissions}
                  showIneligibilityCauses={notEligible}
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

const PaymentsTable = (props: PaymentsTableProps): ReactElement => {
  const { programId } = useBaseUrl();
  const profileParams = {
    businessAreaSlug: props.businessArea,
    program: programId === 'all' ? undefined : programId,
  };
  const { data: profile } = useQuery<Profile>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasUsersProfileRetrieve,
      profileParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasUsersProfileRetrieve(profileParams),
    staleTime: 5 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
  const notEligibleCountParams = {
    businessAreaSlug: props.businessArea,
    programCode: programId,
    paymentPlanPk: props.paymentPlan.id,
  };
  const { data: notEligibleCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsNotEligibleCountRetrieve,
      notEligibleCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsNotEligibleCountRetrieve(
        notEligibleCountParams,
      ),
    enabled: profile?.isSuperuser === true,
  });

  return (
    <>
      <PaymentsTableSection {...props} />
      {profile?.isSuperuser === true && (notEligibleCount?.count || 0) > 0 && (
        <PaymentsTableSection {...props} notEligible />
      )}
    </>
  );
};

export default withErrorBoundary(PaymentsTable, 'PaymentsTable');
