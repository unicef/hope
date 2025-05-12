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
import { headCells } from './PaymentsTableHeadCells';
import { PaymentsTableRow } from './PaymentsTableRow';
import { WarningTooltipTable } from './WarningTooltipTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from 'src/programContext';
import { adjustHeadCells } from '@utils/utils';
import withErrorBoundary from '@components/core/withErrorBoundary';

const StyledBox = styled(Box)`
  background-color: #fff;
`;
interface PaymentsTableProps {
  businessArea: string;
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  permissions: string[];
  canViewDetails?: boolean;
}

function PaymentsTable({
  businessArea,
  paymentPlan,
  permissions,
  canViewDetails = false,
}: PaymentsTableProps): ReactElement {
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const [dialogPayment, setDialogPayment] = useState<
    AllPaymentsForTableQuery['allPayments']['edges'][number]['node'] | null
  >();
  const initialVariables: AllPaymentsForTableQueryVariables = {
    businessArea,
    paymentPlanId: paymentPlan.id,
  };

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
            headCells={adjustedHeadCells}
            query={useAllPaymentsForTableQuery}
            rowsPerPageOptions={[10, 25, 50]}
            queriedObjectName="allPayments"
            initialVariables={initialVariables}
            defaultOrderBy="createdAt"
            defaultOrderDirection="desc"
            renderRow={(row) => (
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
      <WarningTooltipTable
        paymentPlan={paymentPlan}
        payment={dialogPayment}
        setDialogOpen={() => setDialogPayment(null)}
        canViewDetails={canViewDetails}
        baseUrl={baseUrl}
      />
    </>
  );
}

export default withErrorBoundary(PaymentsTable, 'PaymentsTable');
