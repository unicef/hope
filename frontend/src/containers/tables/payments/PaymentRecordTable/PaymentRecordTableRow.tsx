import TableCell from '@mui/material/TableCell';
import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import {
  formatCurrencyWithSymbol,
  householdStatusToColor,
  paymentRecordStatusToColor,
  paymentStatusDisplayMap,
} from '@utils/utils';
import { PaymentRecordNode } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface PaymentRecordTableRowProps {
  paymentRecord: PaymentRecordNode;
  openInNewTab: boolean;
}

export function PaymentRecordTableRow({
  paymentRecord,
  openInNewTab,
}: PaymentRecordTableRowProps): React.ReactElement {
  const { baseUrl } = useBaseUrl();
const navigate = useNavigate()  const paymentRecordPath = `/${baseUrl}/payment-records/${paymentRecord.id}`;
  const handleClick = (): void => {
    if (openInNewTab) {
      window.open(paymentRecordPath);
    } else {
      navigate(paymentRecordPath);
    }
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role="checkbox"
      key={paymentRecord.id}
    >
      <TableCell align="left">
        <BlackLink to={paymentRecordPath}>{paymentRecord.caId}</BlackLink>
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={paymentRecord.status}
          statusToColor={paymentRecordStatusToColor}
          statusNameMapping={paymentStatusDisplayMap}
        />
      </TableCell>
      <AnonTableCell>{paymentRecord.headOfHousehold?.fullName}</AnonTableCell>
      <TableCell align="left">{paymentRecord.household.unicefId}</TableCell>
      <TableCell align="left">
        <StatusBox
          status={paymentRecord.household.status}
          statusToColor={householdStatusToColor}
        />
      </TableCell>
      <TableCell align="left">{paymentRecord.household.size}</TableCell>
      <TableCell align="right">
        {formatCurrencyWithSymbol(
          paymentRecord.entitlementQuantity,
          paymentRecord.currency,
        )}
      </TableCell>
      <TableCell align="right">
        {formatCurrencyWithSymbol(
          paymentRecord.deliveredQuantity,
          paymentRecord.currency,
        )}
      </TableCell>
      <TableCell align="right">
        <UniversalMoment>{paymentRecord.deliveryDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
