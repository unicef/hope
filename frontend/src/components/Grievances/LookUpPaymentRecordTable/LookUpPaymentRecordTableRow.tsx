import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { PaymentRecordNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  decodeIdString,
  formatCurrency,
  paymentRecordStatusToColor,
  verificationRecordsStatusToColor,
} from '../../../utils/utils';
import { ClickableTableRow } from '../../table/ClickableTableRow';
import { StatusBox } from '../../StatusBox';
import { UniversalMoment } from '../../UniversalMoment';
import { Missing } from '../../Missing';
import { Checkbox } from '@material-ui/core';
import { Pointer } from '../../Pointer';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface LookUpPaymentRecordTableRowProps {
  paymentRecord: PaymentRecordNode;
  openInNewTab: boolean;
  selected: Array<string>;
  checkboxClickHandler;
}

export function LookUpPaymentRecordTableRow({
  paymentRecord,
  openInNewTab,
  selected,
  checkboxClickHandler,
}: LookUpPaymentRecordTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();
  const history = useHistory();
  const handleClick = (): void => {
    const path = `/${businessArea}/payment-records/${paymentRecord.id}`;
    if (openInNewTab) {
      window.open(path);
    } else {
      history.push(path);
    }
  };
  const isSelected = (name: string): boolean => selected.includes(name);
  const isItemSelected = isSelected(paymentRecord.id);
  return (
    <ClickableTableRow hover role='checkbox' key={paymentRecord.id}>
      <TableCell padding='checkbox'>
        <Checkbox
          color='primary'
          onClick={(event) => checkboxClickHandler(event, paymentRecord.id)}
          checked={isItemSelected}
          inputProps={{ 'aria-labelledby': paymentRecord.id }}
        />
      </TableCell>
      <TableCell onClick={handleClick} align='left'>
        <Pointer>{decodeIdString(paymentRecord.id)}</Pointer>
      </TableCell>
      <TableCell align='left'>
        {paymentRecord.verifications?.edges[0]?.node.status ? (
          <StatusContainer>
            <StatusBox
              status={paymentRecord.verifications?.edges[0]?.node.status}
              statusToColor={verificationRecordsStatusToColor}
            />
          </StatusContainer>
        ) : (
          '-'
        )}
      </TableCell>
      <TableCell align='left'>{paymentRecord.cashPlan.name}</TableCell>
      <TableCell align='right'>
        {formatCurrency(paymentRecord.deliveredQuantity)}
      </TableCell>
      <TableCell align='right'>
        <Missing />
      </TableCell>
    </ClickableTableRow>
  );
}
