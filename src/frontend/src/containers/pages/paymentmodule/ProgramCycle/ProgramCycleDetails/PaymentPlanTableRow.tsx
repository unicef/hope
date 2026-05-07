import React, { ReactElement } from 'react';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import TableCell from '@mui/material/TableCell';
import { BlackLink } from '@core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { StatusBox } from '@core/StatusBox';
import {
  formatCurrencyWithSymbol,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { UniversalMoment } from '@core/UniversalMoment';
import { LinkedPaymentPlansModal } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/LinkedPaymentPlansModal';
import { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';

interface PaymentPlanTableRowProps {
  paymentPlan: PaymentPlanList;
  canViewDetails: boolean;
}

export const PaymentPlanTableRow = ({
  paymentPlan,
  canViewDetails,
}: PaymentPlanTableRowProps): ReactElement => {
  const { baseUrl } = useBaseUrl();
  const paymentPlanPath = `/${baseUrl}/payment-module/${
    paymentPlan.planType === 'FOLLOW_UP'
      ? 'followup-payment-plans'
      : 'payment-plans'
  }/${paymentPlan.id}`;

  return (
    <ClickableTableRow key={paymentPlan.id}>
      <TableCell align="left">
        {paymentPlan.planType === 'FOLLOW_UP' ? 'Follow-up: ' : ''}
        {canViewDetails ? (
          <BlackLink to={paymentPlanPath}>{paymentPlan.unicefId}</BlackLink>
        ) : (
          paymentPlan.unicefId
        )}
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={paymentPlan.status}
          statusToColor={paymentPlanStatusToColor}
        />
      </TableCell>
      <TableCell align="left">
        {/* //TODO: This link should navigate to the payment plan group details page
        once it's implemented */}
        {paymentPlan.paymentPlanGroup ? (
          <BlackLink
            to={`/${baseUrl}/payment-module/groups/${paymentPlan.paymentPlanGroup.id}`}
          >
            {paymentPlan.paymentPlanGroup.name}
          </BlackLink>
        ) : (
          '-'
        )}
      </TableCell>
      <TableCell align="left">
        {paymentPlan.totalHouseholdsCount || '-'}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(Number(paymentPlan.totalEntitledQuantity), paymentPlan.currency)}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(Number(paymentPlan.totalUndeliveredQuantity), paymentPlan.currency)}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(Number(paymentPlan.totalDeliveredQuantity), paymentPlan.currency)}`}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{paymentPlan.dispersionStartDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{paymentPlan.dispersionEndDate}</UniversalMoment>
      </TableCell>

      <TableCell align="left">
        <LinkedPaymentPlansModal
          paymentPlan={paymentPlan}
          canViewDetails={canViewDetails}
        />
      </TableCell>
    </ClickableTableRow>
  );
};
