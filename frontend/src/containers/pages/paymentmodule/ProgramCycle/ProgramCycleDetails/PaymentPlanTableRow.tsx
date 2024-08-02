import { useCashPlanVerificationStatusChoicesQuery } from '@generated/graphql';
import React from 'react';
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

interface PaymentPlanTableRowProps {
  paymentPlan;
  canViewDetails: boolean;
}

export const PaymentPlanTableRow = ({
  paymentPlan,
  canViewDetails,
}: PaymentPlanTableRowProps): React.ReactElement => {
  const { data: statusChoicesData } =
    useCashPlanVerificationStatusChoicesQuery();

  const paymentPlanPath = `./payment-plans/${paymentPlan.id}`;

  if (!statusChoicesData) return null;

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
        {`${formatCurrencyWithSymbol(paymentPlan.totalEntitledQuantityUSD)}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(paymentPlan.totalUndeliveredQuantityUSD)}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(paymentPlan.totalDeliveredQuantityUSD)}`}
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
