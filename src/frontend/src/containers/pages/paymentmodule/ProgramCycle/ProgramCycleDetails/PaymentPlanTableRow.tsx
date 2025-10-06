import React, { ReactElement } from 'react';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import TableCell from '@mui/material/TableCell';
import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
import {
  formatCurrencyWithSymbol,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { UniversalMoment } from '@core/UniversalMoment';
import { FollowUpPaymentPlansModal } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/FollowUpPaymentPlansModal';
import { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';

interface PaymentPlanTableRowProps {
  paymentPlan: PaymentPlanList;
  canViewDetails: boolean;
}

export const PaymentPlanTableRow = ({
  paymentPlan,
  canViewDetails,
}: PaymentPlanTableRowProps): ReactElement => {
  const paymentPlanPath = `./payment-plans/${paymentPlan.id}`;

  return (
    <ClickableTableRow key={paymentPlan.id}>
      <TableCell align="left">
        {paymentPlan.isFollowUp ? 'Follow-up: ' : ''}
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
        <FollowUpPaymentPlansModal
          paymentPlan={paymentPlan}
          canViewDetails={canViewDetails}
        />
      </TableCell>
    </ClickableTableRow>
  );
};
