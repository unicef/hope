import { Box, Paper, Typography } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { TableWrapper } from '@components/core/TableWrapper';
import { ImportXlsxPaymentPlanPaymentListPerFsp } from '@components/paymentmodule/PaymentPlanDetails/ImportXlsxPaymentPlanPaymentListPerFsp';
import {
  AllPaymentsForTableQuery,
  AllPaymentsForTableQueryVariables,
  PaymentPlanQuery,
  PaymentPlanStatus,
  useAllPaymentsForTableQuery,
} from '@generated/graphql';
import { UniversalTable } from '../../UniversalTable';
import { PeoplePaymentsTableRow } from './PeoplePaymentsTableRow';
import { WarningTooltipTable } from './WarningTooltipTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { headCells } from './PeoplePaymentsTableHeadCells';
import withErrorBoundary from '@components/core/withErrorBoundary';

const StyledBox = styled(Box)`
  background-color: #fff;
`;
interface PeoplePaymentsTableProps {
  businessArea: string;
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  permissions: string[];
  canViewDetails?: boolean;
}

const PeoplePaymentsTable = ({
  businessArea,
  paymentPlan,
  permissions,
  canViewDetails = false,
}: PeoplePaymentsTableProps): ReactElement => {
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const [dialogPayment, setDialogPayment] = useState<
    AllPaymentsForTableQuery['allPayments']['edges'][number]['node'] | null
  >();
  const initialVariables: AllPaymentsForTableQueryVariables = {
    businessArea,
    paymentPlanId: paymentPlan.id,
  };

  return (
    <>
      <TableWrapper>
        <Paper>
          <StyledBox p={6} display="flex" justifyContent="space-between">
            <Typography data-cy="table-title" variant="h6">
              {t('Payee List')}
            </Typography>
            {(paymentPlan.status === PaymentPlanStatus.Accepted ||
              paymentPlan.status === PaymentPlanStatus.Finished) && (
              <ImportXlsxPaymentPlanPaymentListPerFsp
                paymentPlan={paymentPlan}
                permissions={permissions}
              />
            )}
          </StyledBox>
          <UniversalTable<
            AllPaymentsForTableQuery['allPayments']['edges'][number]['node'],
            AllPaymentsForTableQueryVariables
          >
            isOnPaper={false}
            headCells={headCells}
            query={useAllPaymentsForTableQuery}
            rowsPerPageOptions={[10, 25, 50]}
            queriedObjectName="allPayments"
            initialVariables={initialVariables}
            defaultOrderBy="createdAt"
            defaultOrderDirection="desc"
            renderRow={(row) => (
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
