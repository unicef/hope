import { Checkbox, Radio } from '@material-ui/core';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useLocation } from 'react-router-dom';
import {
  formatCurrencyWithSymbol,
  verificationRecordsStatusToColor,
} from '../../../../utils/utils';
import { PaymentRecordAndPaymentNode } from '../../../../__generated__/graphql';
import { BlackLink } from '../../../core/BlackLink';
import { StatusBox } from '../../../core/StatusBox';
import { ClickableTableRow } from '../../../core/Table/ClickableTableRow';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';

interface LookUpPaymentRecordTableRowProps {
  paymentRecord: PaymentRecordAndPaymentNode;
  openInNewTab: boolean;
  selected: Array<string>;
  checkboxClickHandler: (
    event:
      | React.MouseEvent<HTMLButtonElement, MouseEvent>
      | React.MouseEvent<HTMLTableRowElement, MouseEvent>,
    number: string,
  ) => void;
}

export function LookUpPaymentRecordTableRow({
  paymentRecord,
  selected,
  checkboxClickHandler,
}: LookUpPaymentRecordTableRowProps): React.ReactElement {
  const { baseUrl } = useBaseUrl();
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;
  const isSelected = (name: string): boolean => selected.includes(name);
  const isItemSelected = isSelected(paymentRecord.id);
  const received = paymentRecord?.verification?.receivedAmount;

  const renderUrl = (objType): string => {
    if (objType === 'Payment') {
      return `/${baseUrl}/payment-module/payments/${paymentRecord.id}`;
    }
    return `/${baseUrl}/payment-records/${paymentRecord.id}`;
  };

  return (
    <ClickableTableRow
      onClick={(event) => checkboxClickHandler(event, paymentRecord.id)}
      hover
      role='checkbox'
      key={paymentRecord.id}
    >
      <TableCell padding='checkbox'>
        {isEditTicket ? (
          <Radio
            color='primary'
            onClick={(event) => checkboxClickHandler(event, paymentRecord.id)}
            checked={isItemSelected}
            inputProps={{ 'aria-labelledby': paymentRecord.id }}
          />
        ) : (
          <Checkbox
            color='primary'
            onClick={(event) => checkboxClickHandler(event, paymentRecord.id)}
            checked={isItemSelected}
            inputProps={{ 'aria-labelledby': paymentRecord.id }}
          />
        )}
      </TableCell>
      <TableCell align='left'>
        <BlackLink to={renderUrl(paymentRecord.objType)}>
          {paymentRecord.caId}
        </BlackLink>
      </TableCell>
      <TableCell align='left'>
        {paymentRecord.status ? (
          <StatusBox
            status={paymentRecord.status}
            statusToColor={verificationRecordsStatusToColor}
          />
        ) : (
          '-'
        )}
      </TableCell>
      <TableCell align='left'>{paymentRecord.parent.programmeName}</TableCell>
      <TableCell align='right'>
        {formatCurrencyWithSymbol(
          paymentRecord.deliveredQuantity,
          paymentRecord.currency,
        )}
      </TableCell>
      <TableCell align='right'>
        {received === null || received === undefined
          ? '-'
          : formatCurrencyWithSymbol(received, paymentRecord.currency)}
      </TableCell>
    </ClickableTableRow>
  );
}
