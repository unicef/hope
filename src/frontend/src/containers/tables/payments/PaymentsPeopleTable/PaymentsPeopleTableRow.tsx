import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { StatusBox } from '@components/core/StatusBox';
import {
  formatCurrencyWithSymbol,
  paymentRecordStatusToColor,
  paymentStatusDisplayMap,
} from '@utils/utils';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import { PaymentList } from '@restgenerated/models/PaymentList';

interface PaymentsPeopleTableRowProps {
  payment: PaymentList;
  openInNewTab: boolean;
  canViewDetails: boolean;
}

export function PaymentsPeopleTableRow({
  payment,
  openInNewTab,
  canViewDetails,
}: PaymentsPeopleTableRowProps): ReactElement {
  const { baseUrl } = useBaseUrl();
  const navigate = useNavigate();
  const paymentDetailsPath = `/${baseUrl}/payment-module/payments/${payment.id}`;

  const handleClick = (): void => {
    if (openInNewTab) {
      window.open(paymentDetailsPath);
    } else {
      navigate(paymentDetailsPath);
    }
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role="checkbox"
      key={payment.id}
    >
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={paymentDetailsPath}>{payment.unicefId}</BlackLink>
        ) : (
          payment.unicefId
        )}
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={payment.status}
          statusToColor={paymentRecordStatusToColor}
          statusNameMapping={paymentStatusDisplayMap}
        />
      </TableCell>
      <TableCell align="right">
        {formatCurrencyWithSymbol(
          payment.entitlementQuantity,
          payment.currency,
        )}
      </TableCell>
      <TableCell align="right">
        {formatCurrencyWithSymbol(payment.deliveredQuantity, payment.currency)}
      </TableCell>
      <TableCell align="right">
        <UniversalMoment>{payment.deliveryDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
