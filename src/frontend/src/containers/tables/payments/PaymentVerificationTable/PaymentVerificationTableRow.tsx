import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import {
  PaymentPlanNode,
  useCashPlanVerificationStatusChoicesQuery,
} from '@generated/graphql';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import {
  formatCurrencyWithSymbol,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { StatusBox } from '@components/core/StatusBox';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';

interface PaymentVerificationTableRowProps {
  plan: PaymentPlanNode;
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
  const { data: statusChoicesData } =
    useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) return null;

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
          status={plan.status}
          statusToColor={paymentPlanStatusToColor}
        />
      </TableCell>
      <TableCell align="right">
        {formatCurrencyWithSymbol(plan.totalDeliveredQuantity, plan.currency)}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{plan.startDate}</UniversalMoment> -{' '}
        <UniversalMoment>{plan.endDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{plan.updatedAt}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
