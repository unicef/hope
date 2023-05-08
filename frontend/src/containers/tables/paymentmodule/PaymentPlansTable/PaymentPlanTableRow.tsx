import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { BlackLink } from '../../../../components/core/BlackLink';
import { StatusBox } from '../../../../components/core/StatusBox';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import {
  formatCurrencyWithSymbol,
  paymentPlanStatusToColor,
} from '../../../../utils/utils';
import {
  AllPaymentPlansForTableQuery,
  useCashPlanVerificationStatusChoicesQuery,
} from '../../../../__generated__/graphql';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface PaymentVerificationTableRowProps {
  plan: AllPaymentPlansForTableQuery['allPaymentPlans']['edges'][number]['node'];
  canViewDetails: boolean;
}

export const PaymentPlanTableRow = ({
  plan,
  canViewDetails,
}: PaymentVerificationTableRowProps): React.ReactElement => {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const paymentPlanPath = `/${businessArea}/payment-module/${
    plan.isFollowUp ? 'followup-payment-plans' : 'payment-plans'
  }/${plan.id}`;
  const handleClick = (): void => {
    history.push(paymentPlanPath);
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
    >
      <TableCell align='left'>
        {plan.isFollowUp ? 'Follow-up: ' : ''}
        {canViewDetails ? (
          <BlackLink to={paymentPlanPath}>{plan.unicefId}</BlackLink>
        ) : (
          plan.unicefId
        )}
      </TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={plan.status}
            statusToColor={paymentPlanStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>{plan.totalHouseholdsCount || '-'}</TableCell>
      <TableCell align='left'>{plan.currencyName}</TableCell>
      <TableCell align='right'>
        {`${formatCurrencyWithSymbol(
          plan.totalEntitledQuantity,
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align='right'>
        {`${formatCurrencyWithSymbol(
          plan.totalDeliveredQuantity,
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align='right'>
        {`${formatCurrencyWithSymbol(
          plan.totalUndeliveredQuantity,
          plan.currency,
        )}`}
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{plan.dispersionStartDate}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{plan.dispersionEndDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
};
