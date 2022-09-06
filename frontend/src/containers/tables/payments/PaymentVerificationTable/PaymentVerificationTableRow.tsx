import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import {
  AllCashPlansQuery,
  useCashPlanVerificationStatusChoicesQuery,
} from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import {
  choicesToDict,
  formatCurrencyWithSymbol,
  paymentVerificationStatusToColor,
} from '../../../../utils/utils';
import { StatusBox } from '../../../../components/core/StatusBox';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { BlackLink } from '../../../../components/core/BlackLink';

interface PaymentVerificationTableRowProps {
  plan: AllCashPlansQuery['allCashPlans']['edges'][number]['node'];
  canViewDetails: boolean;
}

export function PaymentVerificationTableRow({
  plan,
  canViewDetails,
}: PaymentVerificationTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const paymentVerificationPlanPath = `/${businessArea}/payment-verification/${plan.id}`;
  const handleClick = (): void => {
    history.push(paymentVerificationPlanPath);
  };
  const {
    data: statusChoicesData,
  } = useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) return null;
  const deliveryTypeChoicesDict = choicesToDict(
    statusChoicesData.paymentRecordDeliveryTypeChoices,
  );

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
          <BlackLink to={paymentVerificationPlanPath}>{plan.caId}</BlackLink>
        ) : (
          plan.caId
        )}
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={plan.cashPlanPaymentVerificationSummary.status}
          statusToColor={paymentVerificationStatusToColor}
        />
      </TableCell>
      <TableCell align='left'>
        {plan.serviceProvider?.fullName || '-'}
      </TableCell>
      <TableCell align='left'>
        {deliveryTypeChoicesDict[plan.deliveryType]}
      </TableCell>
      <TableCell align='right'>
        {formatCurrencyWithSymbol(plan.totalDeliveredQuantity, plan.currency)}
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{plan.startDate}</UniversalMoment> -{' '}
        <UniversalMoment>{plan.endDate}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>{plan.program.name}</TableCell>
      <TableCell align='left'>
        <UniversalMoment>{plan.updatedAt}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
