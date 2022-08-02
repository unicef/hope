import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import {
  AllPaymentPlansQuery,
  useCashPlanVerificationStatusChoicesQuery,
} from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import {
  choicesToDict,
  formatCurrency,
  paymentVerificationStatusToColor,
} from '../../../../utils/utils';
import { StatusBox } from '../../../../components/core/StatusBox';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { BlackLink } from '../../../../components/core/BlackLink';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
interface PaymentVerificationTableRowProps {
  plan: AllPaymentPlansQuery['allPaymentPlans']['edges'][number]['node'];
  canViewDetails: boolean;
}

export const PaymentPlanTableRow = ({
  plan,
  canViewDetails,
}: PaymentVerificationTableRowProps): React.ReactElement => {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const paymentPlanPath = `/${businessArea}/payment-module/payment-plans/${plan.id}`;
  const handleClick = (): void => {
    history.push(paymentPlanPath);
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
          <BlackLink to={paymentPlanPath}>{plan.id.slice(0, 10)}</BlackLink>
        ) : (
          plan.id.slice(0, 10)
        )}
      </TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={plan.status}
            statusToColor={paymentVerificationStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>
        {plan.totalHouseholdsCount || '-'}
      </TableCell>
      <TableCell align='left'>
        {plan.currency}
      </TableCell>
      <TableCell align='right'>
        {formatCurrency(plan.totalEntitledQuantity, true)}
      </TableCell>
      <TableCell align='right'>
        {formatCurrency(plan.totalDeliveredQuantity, true)}
      </TableCell>
      <TableCell align='right'>
        {formatCurrency(plan.totalUndeliveredQuantity, true)}
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
