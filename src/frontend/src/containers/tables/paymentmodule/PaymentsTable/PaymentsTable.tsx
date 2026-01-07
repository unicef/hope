import { TableWrapper } from '@components/core/TableWrapper';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { ImportXlsxPaymentPlanPaymentListPerFsp } from '@components/paymentmodule/PaymentPlanDetails/ImportXlsxPaymentPlanPaymentListPerFsp';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box, Paper, Typography } from '@mui/material';
import { createApiParams } from '@utils/apiUtils';
import { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { adjustHeadCells, getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { headCells } from './PaymentsTableHeadCells';
import { PaymentsTableRow } from './PaymentsTableRow';
import { WarningTooltipTable } from './WarningTooltipTable';
import { PaymentsFilters } from './PaymentsFilters';
import { PaymentList } from '@restgenerated/models/PaymentList';
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
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const initialFilter = {
    householdUnicefId: '',
    collectorFullname: '',
    paymentUnicefId: '',
  };

  const [dialogPayment, setDialogPayment] = useState<PaymentList | null>(null);
  const location = useLocation();
  const [page, setPage] = useState(0);

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

  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      programSlug: programId,
      householdUnicefId: appliedFilter.householdUnicefId || null,
      collectorFullname: appliedFilter.collectorFullname || null,
      paymentUnicefId: appliedFilter.paymentUnicefId || null,
    }),
    [
      businessArea,
      programId,
      appliedFilter.householdUnicefId,
      appliedFilter.collectorFullname,
      appliedFilter.paymentUnicefId,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const {
    data: paymentsData,
    isLoading,
    error,
  } = useQuery<PaginatedPaymentListList>({
    queryKey: [
      'businessAreasProgramsPaymentPlansPaymentsList',
      queryVariables,
      businessArea,
      programId,
      paymentPlan.id,
    ],
    queryFn: () => {
      return RestService.restBusinessAreasProgramsPaymentPlansPaymentsList(
        createApiParams(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
            paymentPlanPk: paymentPlan.id,
          },
          { ...queryVariables },
          { withPagination: true },
        ),
      );
    },
  });

  // Payments count
  const { data: paymentsCount } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsPaymentsCountRetrieve',
      businessArea,
      programId,
      paymentPlan.id,
      queryVariables,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsCountRetrieve(
        createApiParams(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
            paymentPlanPk: paymentPlan.id,
          },
          { ...queryVariables },
        ),
      ),
    // fetch count only on the first page and persist it across pages
    enabled: !!businessArea && !!paymentPlan?.id && page === 0,
  });

  const itemsCount = usePersistedCount(page, paymentsCount);

  const replacements = {
    household__unicef_id: (_beneficiaryGroup) =>
      `${_beneficiaryGroup?.groupLabel} ${t('ID')}`,
    household__size: (_beneficiaryGroup) =>
      `${_beneficiaryGroup?.groupLabel} ${t('Size')}`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
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
      <Box p={4}>
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
            <StyledBox p={6} display="flex" justifyContent="space-between">
              <Typography data-cy="table-title" variant="h6">
                {t('Payee List')}
              </Typography>
              {(paymentPlan.status === PaymentPlanStatusEnum.ACCEPTED ||
                paymentPlan.status === PaymentPlanStatusEnum.FINISHED) && (
                <ImportXlsxPaymentPlanPaymentListPerFsp
                  paymentPlan={paymentPlan}
                  permissions={permissions}
                />
              )}
            </StyledBox>
            <UniversalRestTable
              isOnPaper={false}
              headCells={adjustedHeadCells}
              rowsPerPageOptions={[10, 25, 50]}
              defaultOrderBy="createdAt"
              defaultOrderDirection="desc"
              isLoading={isLoading}
              error={error}
              queryVariables={queryVariables}
              setQueryVariables={setQueryVariables}
              data={paymentsData}
              itemsCount={itemsCount}
              page={page}
              setPage={setPage}
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
