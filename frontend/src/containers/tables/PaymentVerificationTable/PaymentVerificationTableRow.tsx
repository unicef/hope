import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { Link, useHistory } from 'react-router-dom';
import styled from 'styled-components';
import {
  AllCashPlansQuery,
  useCashPlanVerificationStatusChoicesQuery,
} from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import {
  choicesToDict,
  formatCurrencyWithSymbol,
  paymentVerificationStatusToColor,
} from '../../../utils/utils';
import { StatusBox } from '../../../components/StatusBox';
import { UniversalMoment } from '../../../components/UniversalMoment';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
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
    >
      <TableCell align='left'>
        {canViewDetails ? (
          <Link
            target='_blank'
            rel='noopener noreferrer'
            to={paymentVerificationPlanPath}
          >
            {plan.caId}
          </Link>
        ) : (
          plan.caId
        )}
      </TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={plan.verificationStatus}
            statusToColor={paymentVerificationStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>{plan.serviceProvider?.fullName}</TableCell>
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
