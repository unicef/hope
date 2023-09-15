import { TableCell } from '@material-ui/core';
import React from 'react';
import { useCashPlanVerificationStatusChoicesQuery } from '../../../../../__generated__/graphql';
import { BlackLink } from '../../../../../components/core/BlackLink';
import { StatusBox } from '../../../../../components/core/StatusBox';
import { ClickableTableRow } from '../../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../../components/core/UniversalMoment';
import { useBaseUrl } from '../../../../../hooks/useBaseUrl';
import {
  paymentPlanStatusToColor,
  formatCurrencyWithSymbol,
} from '../../../../../utils/utils';
import { PaymentPlansTableFollowUpPaymentPlansModal } from './PaymentPlansTableFollowUpPaymentPlansModal';

interface PaymentPlanTableRowProgramCycleProps {
  plan;
  canViewDetails: boolean;
}

export const PaymentPlanTableRowProgramCycle = ({
  plan,
  canViewDetails,
}: PaymentPlanTableRowProgramCycleProps): React.ReactElement => {
  const { baseUrl } = useBaseUrl();
  const paymentPlanPath = `/${baseUrl}/payment-module/program-cycles/${
    plan.programCycle.id
  }/${plan.isFollowUp ? 'followup-payment-plans' : 'payment-plans'}/${plan.id}`;

  const {
    data: statusChoicesData,
  } = useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) return null;

  return (
    <ClickableTableRow key={plan.id}>
      <TableCell align='left'>
        {plan.isFollowUp ? 'Follow-up: ' : ''}
        {canViewDetails ? (
          <BlackLink to={paymentPlanPath}>{plan.unicefId}</BlackLink>
        ) : (
          plan.unicefId
        )}
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={plan.status}
          statusToColor={paymentPlanStatusToColor}
        />
      </TableCell>
      <TableCell align='left'>{plan.totalHouseholdsCount || '-'}</TableCell>
      <TableCell align='right'>
        {`${formatCurrencyWithSymbol(plan.totalEntitledQuantityUSD)}`}
      </TableCell>
      <TableCell align='right'>
        {`${formatCurrencyWithSymbol(plan.totalUndeliveredQuantityUSD)}`}
      </TableCell>
      <TableCell align='right'>
        {`${formatCurrencyWithSymbol(plan.totalDeliveredQuantityUSD)}`}
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{plan.dispersionStartDate}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{plan.dispersionEndDate}</UniversalMoment>
      </TableCell>

      <TableCell align='left'>
        <PaymentPlansTableFollowUpPaymentPlansModal
          paymentPlan={plan}
          canViewDetails={canViewDetails}
        />
      </TableCell>
    </ClickableTableRow>
  );
};
