import { Checkbox } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { formatCurrencyWithSymbol, paymentStatusToColor } from '@utils/utils';
import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import { MouseEvent, ReactElement } from 'react';
import { PaymentList } from '@restgenerated/models/PaymentList';

interface LookUpPaymentRecordTableRowProps {
  paymentRecord: PaymentList;
  openInNewTab: boolean;
  selected: Array<PaymentList>;
  checkboxClickHandler: (
    event: MouseEvent<HTMLTableRowElement> | MouseEvent<HTMLButtonElement>,
    selectedPaymentRecord: PaymentList,
  ) => void;
}

export function LookUpPaymentRecordTableRow({
  paymentRecord,
  selected,
  checkboxClickHandler,
}: LookUpPaymentRecordTableRowProps): ReactElement {
  const { baseUrl, isAllPrograms } = useBaseUrl();
  const isItemSelected = (item): boolean =>
    selected.some((selectedItem) => selectedItem.id === item.id);
  const paymentRecordIsSelected = isItemSelected(paymentRecord);
  const received = paymentRecord?.verification?.receivedAmount;
  const renderUrl = (): string => {
    return `/${baseUrl}/payment-module/payments/${paymentRecord.id}`;
  };
  const url = renderUrl();

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
          <BlackLink to={url}>{paymentRecord.unicefId}</BlackLink>
        ) : (
          <span>{paymentRecord.unicefId}</span>
        )}
      </TableCell>
      <TableCell align="left">
        {paymentRecord.status ? (
          <StatusBox
            status={paymentRecord.status}
            statusToColor={paymentStatusToColor}
          />
        ) : (
          '-'
        )}
      </TableCell>
      <TableCell align="left">{paymentRecord.programName}</TableCell>
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
