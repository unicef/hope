import { useCashPlanVerificationStatusChoicesQuery } from '@generated/graphql';
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
  const { data: statusChoicesData } =
    useCashPlanVerificationStatusChoicesQuery();

  const paymentPlanPath = `./payment-plans/${paymentPlan.id}`;

  if (!statusChoicesData) return null;

  return (
    <ClickableTableRow key={paymentPlan.id}>
      <TableCell align="left">
        {paymentPlan.is_follow_up ? 'Follow-up: ' : ''}
        {canViewDetails ? (
          <BlackLink to={paymentPlanPath}>{paymentPlan.unicef_id}</BlackLink>
        ) : (
          paymentPlan.unicef_id
        )}
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={paymentPlan.status}
          statusToColor={paymentPlanStatusToColor}
        />
      </TableCell>
      <TableCell align="left">
        {paymentPlan.total_households_count || '-'}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(Number(paymentPlan.total_entitled_quantity), paymentPlan.currency)}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(Number(paymentPlan.total_undelivered_quantity), paymentPlan.currency)}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(Number(paymentPlan.total_delivered_quantity), paymentPlan.currency)}`}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{paymentPlan.dispersion_start_date}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{paymentPlan.dispersion_end_date}</UniversalMoment>
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
