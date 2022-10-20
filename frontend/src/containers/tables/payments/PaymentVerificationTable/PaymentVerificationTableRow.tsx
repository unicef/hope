import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import {
  CashPlanAndPaymentPlanNode,
  useCashPlanVerificationStatusChoicesQuery,
} from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import {
  formatCurrencyWithSymbol,
  paymentVerificationStatusToColor,
} from '../../../../utils/utils';
import { StatusBox } from '../../../../components/core/StatusBox';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { BlackLink } from '../../../../components/core/BlackLink';

interface PaymentVerificationTableRowProps {
  plan: CashPlanAndPaymentPlanNode;
  canViewDetails: boolean;
}

export function PaymentVerificationTableRow({
  plan,
  canViewDetails,
}: PaymentVerificationTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const planVerificationPath = `/${businessArea}/payment-verification/${plan.objType === "CashPlan" ? "cash-plan" : "payment-plan"}/${plan.id}`;
  const handleClick = (): void => {
    history.push(planVerificationPath);
  };
  const {
    data: statusChoicesData,
  } = useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) return null;

  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={plan.id}
      data-cy='cash-plan-table-row'
    >
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={planVerificationPath}>{plan.unicefId}</BlackLink>
        ) : (
          plan.unicefId
        )}
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={plan.verificationStatus}
          statusToColor={paymentVerificationStatusToColor}
        />
      </TableCell>
      <TableCell align='right'>
        {formatCurrencyWithSymbol(plan.totalDeliveredQuantity, plan.currency)}
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{plan.startDate}</UniversalMoment> -{' '}
        <UniversalMoment>{plan.endDate}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>{plan.programmeName}</TableCell>
      <TableCell align='left'>
        <UniversalMoment>{plan.updatedAt}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
