import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import Moment from 'react-moment';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { CashPlanNode, PaymentRecordNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { StatusBox } from '../../../components/StatusBox';
import { cashPlanStatusToColor, paymentRecordStatusToColor } from '../../../utils/utils';

const StatusContainer = styled.div`
  width: 120px;
`;

interface PaymentRecordTableRowProps {
  paymentRecord: PaymentRecordNode;
}

export function RegistrationDataImportTableRow({ paymentRecord }: PaymentRecordTableRowProps) {
  const history = useHistory();
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/payment_records/${paymentRecord.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={paymentRecord.id}
    >
      <TableCell align='left'>{paymentRecord.cashAssistId}</TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={paymentRecord.status}
            statusToColor={paymentRecordStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>{paymentRecord.headOfHousehold}</TableCell>
      <TableCell align='left'>{paymentRecord.household.householdCaId}</TableCell>
      <TableCell align='left'>{paymentRecord.totalPersonCovered}</TableCell>
      <TableCell align='right'>
        {paymentRecord.entitlement.entitlementQuantity.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}
      </TableCell>
      <TableCell align='right'>
        {paymentRecord.entitlement.deliveredQuantity.toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}
      </TableCell>
      <TableCell align='right'>
        <Moment format='MM/DD/YYYY'>
          {paymentRecord.entitlement.deliveryDate}
        </Moment>
      </TableCell>
    </ClickableTableRow>
  );
}
