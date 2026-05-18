import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { LinkedPaymentPlansModal } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/LinkedPaymentPlansModal';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { TableCell } from '@mui/material';
import { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';
import {
  formatCurrencyWithSymbol,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { ReactElement } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';

interface PaymentPlanTableRowProps {
  plan: PaymentPlanList;
  canViewDetails: boolean;
}

export const PaymentPlanTableRow = ({
  plan,
  canViewDetails,
}: PaymentPlanTableRowProps): ReactElement => {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const { isSocialDctType } = useProgramContext();
  const paymentPlanPath = `/${baseUrl}/payment-module/${
    plan.planType === 'FOLLOW_UP' ? 'followup-payment-plans' : 'payment-plans'
  }/${plan.id}`;
  const handleClick = (): void => {
    navigate(paymentPlanPath);
  };

  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role="checkbox"
      key={plan.id}
    >
      <TableCell align="left">
        {plan.planType === 'FOLLOW_UP' ? 'Follow-up: ' : ''}
        {canViewDetails ? (
          <BlackLink to={paymentPlanPath}>{plan.unicefId}</BlackLink>
        ) : (
          plan.unicefId
        )}
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={plan.status}
          statusToColor={paymentPlanStatusToColor}
        />
      </TableCell>
      <TableCell align="left">
        {plan.paymentPlanGroup ? (
          <BlackLink to={`/${baseUrl}/payment-module/groups/${plan.paymentPlanGroup.id}`}>
            {plan.paymentPlanGroup.name}
          </BlackLink>
        ) : '-'}
      </TableCell>
      <TableCell align="left">{plan.name}</TableCell>
      <TableCell align="left">
        {isSocialDctType
          ? plan.totalIndividualsCount || '-'
          : plan.totalHouseholdsCount || '-'}
      </TableCell>
      <TableCell align="left">{plan.currency}</TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(
          Number(plan.totalEntitledQuantity),
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(
          Number(plan.totalDeliveredQuantity),
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align="right">
        {`${formatCurrencyWithSymbol(
          Number(plan.totalUndeliveredQuantity),
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{plan.dispersionStartDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{plan.dispersionEndDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        <LinkedPaymentPlansModal
          paymentPlan={plan}
          canViewDetails={canViewDetails}
        />
      </TableCell>
    </ClickableTableRow>
  );
};
