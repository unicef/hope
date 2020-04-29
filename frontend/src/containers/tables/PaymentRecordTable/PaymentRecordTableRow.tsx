import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import Moment from 'react-moment';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { PaymentRecordNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { StatusBox } from '../../../components/StatusBox';
import {
  decodeIdString,
  formatCurrency,
  paymentRecordStatusToColor,
} from '../../../utils/utils';

const StatusContainer = styled.div`
  width: 120px;
`;

interface PaymentRecordTableRowProps {
  paymentRecord: PaymentRecordNode;
  openInNewTab: boolean;
}

export function PaymentRecordTableRow({
  paymentRecord,
  openInNewTab,
}: PaymentRecordTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();
  const history = useHistory();
  const handleClick = (): void => {
    const path = `/${businessArea}/payment_records/${paymentRecord.id}`;
    if (openInNewTab) {
      window.open(path);
    } else {
      history.push(path);
    }
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
      <TableCell align='left'>
        {decodeIdString(paymentRecord.household.id)}
      </TableCell>
      <TableCell align='left'>{paymentRecord.totalPersonCovered}</TableCell>
      <TableCell align='right'>
        {formatCurrency(paymentRecord.entitlement.entitlementQuantity)}
      </TableCell>
      <TableCell align='right'>
        {formatCurrency(paymentRecord.entitlement.deliveredQuantity)}
      </TableCell>
      <TableCell align='right'>
        <Moment format='DD/MM/YYYY'>
          {paymentRecord.entitlement.deliveryDate}
        </Moment>
      </TableCell>
    </ClickableTableRow>
  );
}
