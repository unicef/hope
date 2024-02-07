import { Checkbox } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import * as React from 'react';
import { PaymentRecordAndPaymentNode } from '../../../../__generated__/graphql';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import {
  formatCurrencyWithSymbol,
  verificationRecordsStatusToColor,
} from '@utils/utils';
import { BlackLink } from '../../../core/BlackLink';
import { StatusBox } from '../../../core/StatusBox';
import { ClickableTableRow } from '../../../core/Table/ClickableTableRow';

interface LookUpPaymentRecordTableRowProps {
  paymentRecord: PaymentRecordAndPaymentNode;
  openInNewTab: boolean;
  selected: Array<PaymentRecordAndPaymentNode>;
  checkboxClickHandler: (
    event:
      | React.MouseEvent<HTMLButtonElement, MouseEvent>
      | React.MouseEvent<HTMLTableRowElement, MouseEvent>,
    selectedPaymentRecord: PaymentRecordAndPaymentNode,
  ) => void;
}

export function LookUpPaymentRecordTableRow({
  paymentRecord,
  selected,
  checkboxClickHandler,
}: LookUpPaymentRecordTableRowProps): React.ReactElement {
  const { baseUrl, isAllPrograms } = useBaseUrl();
  const isItemSelected = (item): boolean =>
    selected.some((selectedItem) => selectedItem.id === item.id);
  const paymentRecordIsSelected = isItemSelected(paymentRecord);
  const received = paymentRecord?.verification?.receivedAmount;
  const renderUrl = (objType): string => {
    if (objType === 'Payment') {
      return `/${baseUrl}/payment-module/payments/${paymentRecord.id}`;
    }
    return `/${baseUrl}/payment-records/${paymentRecord.id}`;
  };

  return (
    <ClickableTableRow
      onClick={(event) => checkboxClickHandler(event, paymentRecord)}
      hover
      role="checkbox"
      key={paymentRecord.id}
    >
      <TableCell padding="checkbox">
        <Checkbox
          color="primary"
          onClick={(event) => checkboxClickHandler(event, paymentRecord)}
          checked={paymentRecordIsSelected}
          inputProps={{ 'aria-labelledby': paymentRecord.id }}
        />
      </TableCell>
      <TableCell align="left">
        {!isAllPrograms ? (
          <BlackLink to={renderUrl(paymentRecord.objType)}>
            {paymentRecord.caId}
          </BlackLink>
        ) : (
          <span>{paymentRecord.caId}</span>
        )}
      </TableCell>
      <TableCell align="left">
        {paymentRecord.status ? (
          <StatusBox
            status={paymentRecord.status}
            statusToColor={verificationRecordsStatusToColor}
          />
        ) : (
          '-'
        )}
      </TableCell>
      <TableCell align="left">{paymentRecord.parent.programName}</TableCell>
      <TableCell align="right">
        {formatCurrencyWithSymbol(
          paymentRecord.deliveredQuantity,
          paymentRecord.currency,
        )}
      </TableCell>
      <TableCell align="right">
        {received === null || received === undefined
          ? '-'
          : formatCurrencyWithSymbol(received, paymentRecord.currency)}
      </TableCell>
    </ClickableTableRow>
  );
}
