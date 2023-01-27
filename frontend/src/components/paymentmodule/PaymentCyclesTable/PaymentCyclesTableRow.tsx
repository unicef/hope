import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  formatCurrencyWithSymbol,
  paymentCycleStatusToColor,
} from '../../../utils/utils';
import { useCashPlanVerificationStatusChoicesQuery } from '../../../__generated__/graphql';
import { BlackLink } from '../../core/BlackLink';
import { StatusBox } from '../../core/StatusBox';
import { ClickableTableRow } from '../../core/Table/ClickableTableRow';
import { UniversalMoment } from '../../core/UniversalMoment';

interface PaymentCyclesTableRowProps {
  cycle: AllPaymentCyclesForTableQuery['allPaymentCycles']['edges'][number]['node'];
  canViewDetails: boolean;
}

export const PaymentCyclesTableRow = ({
  cycle,
  canViewDetails,
}: PaymentCyclesTableRowProps): React.ReactElement => {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const paymentCyclePath = `/${businessArea}/payment-module/payment-cycles/${cycle.id}`;
  const handleClick = (): void => {
    history.push(paymentCyclePath);
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
      key={cycle.id}
    >
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={paymentCyclePath}>{cycle.unicefId}</BlackLink>
        ) : (
          cycle.unicefId
        )}
      </TableCell>
      <TableCell align='left'>{cycle.title}</TableCell>

      <TableCell align='left'>
        <StatusBox
          status={cycle.status}
          statusToColor={paymentCycleStatusToColor}
        />
      </TableCell>
      <TableCell align='right'>
        {`${formatCurrencyWithSymbol(cycle.totalEntitledQuantity, 'USD')}`}
      </TableCell>
      <TableCell align='right'>
        {`${formatCurrencyWithSymbol(cycle.totalUndeliveredQuantity, 'USD')}`}
      </TableCell>
      <TableCell align='right'>
        {`${formatCurrencyWithSymbol(cycle.totalDeliveredQuantity, 'USD')}`}
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{cycle.startDate}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{cycle.endDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
};
