import { Box, Paper, Typography } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { TableWrapper } from '../../../../components/core/TableWrapper';
import { ImportXlsxPaymentPlanPaymentListPerFsp } from '../../../../components/paymentmodule/PaymentPlanDetails/ImportXlsxPaymentPlanPaymentListPerFsp';
import {
  AllPaymentsForTableQuery,
  AllPaymentsForTableQueryVariables,
  PaymentPlanQuery,
  PaymentPlanStatus,
  useAllPaymentsForTableQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './PaymentsTableHeadCells';
import { PaymentsTableRow } from './PaymentsTableRow';
import { WarningTooltipTable } from './WarningTooltipTable';

const StyledBox = styled(Box)`
  background-color: #fff;
`;
interface PaymentsTableProps {
  businessArea: string;
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canViewDetails?: boolean;
}

export const PaymentsTable = ({
  businessArea,
  paymentPlan,
  canViewDetails = false,
}: PaymentsTableProps): React.ReactElement => {
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
          <StyledBox p={6} display='flex' justifyContent='space-between'>
            <Typography data-cy='table-title' variant='h6'>
              {t('Payments List')}
            </Typography>
            {paymentPlan.status === PaymentPlanStatus.Accepted && (
              <ImportXlsxPaymentPlanPaymentListPerFsp
                paymentPlan={paymentPlan}
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
            queriedObjectName='allPayments'
            initialVariables={initialVariables}
            defaultOrderBy='createdAt'
            defaultOrderDirection='desc'
            renderRow={(row) => (
              <PaymentsTableRow
                key={row.id}
                payment={row}
                canViewDetails={canViewDetails}
                onWarningClick={(payment) => {
                  setDialogPayment(payment);
                }}
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
        businessArea={businessArea}
      />
    </>
  );
};
