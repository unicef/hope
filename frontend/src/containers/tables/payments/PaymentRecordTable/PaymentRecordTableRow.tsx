import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { BlackLink } from '../../../../components/core/BlackLink';
import { StatusBox } from '../../../../components/core/StatusBox';
import { AnonTableCell } from '../../../../components/core/Table/AnonTableCell';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import {
  formatCurrencyWithSymbol,
  householdStatusToColor,
  paymentRecordStatusToColor,
} from '../../../../utils/utils';
import { PaymentRecordNode } from '../../../../__generated__/graphql';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';

interface PaymentRecordTableRowProps {
  paymentRecord: PaymentRecordNode;
  openInNewTab: boolean;
}

export function PaymentRecordTableRow({
  paymentRecord,
  openInNewTab,
}: PaymentRecordTableRowProps): React.ReactElement {
  const { baseUrl } = useBaseUrl();
  const history = useHistory();
  const paymentRecordPath = `/${baseUrl}/payment-records/${paymentRecord.id}`;
  const handleClick = (): void => {
    if (openInNewTab) {
      window.open(paymentRecordPath);
    } else {
      history.push(paymentRecordPath);
    }
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={paymentRecord.id}
    >
      <TableCell align='left'>
        <BlackLink to={paymentRecordPath}>{paymentRecord.caId}</BlackLink>
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={paymentRecord.status}
          statusToColor={paymentRecordStatusToColor}
        />
      </TableCell>
      <AnonTableCell>{paymentRecord.headOfHousehold?.fullName}</AnonTableCell>
      <TableCell align='left'>{paymentRecord.household.unicefId}</TableCell>
      <TableCell align='left'>
        <StatusBox
          status={paymentRecord.household.status}
          statusToColor={householdStatusToColor}
        />
      </TableCell>
      <TableCell align='left'>{paymentRecord.household.size}</TableCell>
      <TableCell align='right'>
        {formatCurrencyWithSymbol(
          paymentRecord.entitlementQuantity,
          paymentRecord.currency,
        )}
      </TableCell>
      <TableCell align='right'>
        {formatCurrencyWithSymbol(
          paymentRecord.deliveredQuantity,
          paymentRecord.currency,
        )}
      </TableCell>
      <TableCell align='right'>
        <UniversalMoment>{paymentRecord.deliveryDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
