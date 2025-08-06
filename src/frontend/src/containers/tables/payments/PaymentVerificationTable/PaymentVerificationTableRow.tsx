import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import TableCell from '@mui/material/TableCell';
import {
  formatCurrencyWithSymbol,
  paymentVerificationStatusToColor,
} from '@utils/utils';
import { ReactElement } from 'react';
import { useNavigate } from 'react-router-dom';
import type { PaymentVerificationPlanList } from '@restgenerated/models/PaymentVerificationPlanList';

interface PaymentVerificationTableRowProps {
  plan: PaymentVerificationPlanList;
  canViewDetails: boolean;
}

export function PaymentVerificationTableRow({
  plan,
  canViewDetails,
}: PaymentVerificationTableRowProps): ReactElement {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const planVerificationPath = `/${baseUrl}/payment-verification/payment-plan/${plan.id}`;
  const handleClick = (): void => {
    navigate(planVerificationPath);
  };

  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role="checkbox"
      key={plan.id}
      data-cy="cash-plan-table-row"
    >
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={planVerificationPath}>{plan.unicefId}</BlackLink>
        ) : (
          plan.unicefId
        )}
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={plan?.verificationStatus}
          statusToColor={paymentVerificationStatusToColor}
        />
      </TableCell>
      <TableCell align="right">
        {formatCurrencyWithSymbol(plan.totalDeliveredQuantity, plan.currency)}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{plan.dispersionStartDate}</UniversalMoment> -{' '}
        <UniversalMoment>{plan.dispersionEndDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left" data-cy="cycle-title">
        {plan?.programCycleTitle || '-'}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{plan.updatedAt}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
