import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import {AllCashPlansQuery, AllCashPlansQueryResult, CashPlanNode, useCashPlanVerificationStatusChoicesQuery} from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import {
  choicesToDict,
  decodeIdString,
  formatCurrency,
  paymentVerificationStatusToColor,
} from '../../../utils/utils';
import { StatusBox } from '../../../components/StatusBox';
import { UniversalMoment } from '../../../components/UniversalMoment';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
interface PaymentVerificationTableRowProps {
  plan: AllCashPlansQuery["allCashPlans"]["edges"][number]["node"];
}

export function PaymentVerificationTableRow({
  plan,
}: PaymentVerificationTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const handleClick = (): void => {
    const path = `/${businessArea}/payment-verification/${plan.id}`;
    history.push(path);
  };
  const {
    data: statusChoicesData,
  } = useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) {
    return null;
  }
  const deliveryTypeChoicesDict = choicesToDict(
    statusChoicesData.paymentRecordDeliveryTypeChoices,
  );

  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={plan.id}
    >
      <TableCell align='left'>{decodeIdString(plan.id)}</TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={plan.verificationStatus}
            statusToColor={paymentVerificationStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>{plan.assistanceThrough}</TableCell>
      <TableCell align='left'>{deliveryTypeChoicesDict[plan.deliveryType]}</TableCell>
      <TableCell align='right'>
        {formatCurrency(plan.totalDeliveredQuantity)}
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
