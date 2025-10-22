import { TableWrapper } from '@components/core/TableWrapper';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { ImportXlsxPaymentPlanPaymentListPerFsp } from '@components/paymentmodule/PaymentPlanDetails/ImportXlsxPaymentPlanPaymentListPerFsp';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box, Paper, Typography } from '@mui/material';
import { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';
import { PaymentList } from '@restgenerated/models/PaymentList';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { headCells } from './PeoplePaymentsTableHeadCells';
import { PeoplePaymentsTableRow } from './PeoplePaymentsTableRow';
import { WarningTooltipTable } from './WarningTooltipTable';
import { createApiParams } from '@utils/apiUtils';

const StyledBox = styled(Box)`
  background-color: #fff;
`;
interface PeoplePaymentsTableProps {
  businessArea: string;
  paymentPlan: PaymentPlanDetail;
  permissions: string[];
  canViewDetails?: boolean;
}

const PeoplePaymentsTable = ({
  businessArea,
  paymentPlan,
  permissions,
  canViewDetails = false,
}: PeoplePaymentsTableProps): ReactElement => {
  const { baseUrl, programId } = useBaseUrl();
  const { t } = useTranslation();

  const [dialogPayment, setDialogPayment] = useState<PaymentList | null>(null);
  const initialQueryVariables = {
    businessAreaSlug: businessArea,
    programSlug: programId,
    paymentPlanId: paymentPlan.id,
  };
  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  const [page, setPage] = useState(0);

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
          queryVariables,
          { withPagination: true },
        ),
      );
    },
  });

  return (
    <>
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
            headCells={headCells}
            rowsPerPageOptions={[10, 25, 50]}
            defaultOrderBy="createdAt"
            defaultOrderDirection="desc"
            isLoading={isLoading}
            error={error}
            queryVariables={queryVariables}
            setQueryVariables={setQueryVariables}
            data={paymentsData}
            page={page}
            setPage={setPage}
            renderRow={(row: PaymentList) => (
              <PeoplePaymentsTableRow
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
export default withErrorBoundary(PeoplePaymentsTable, 'PeoplePaymentsTable');
