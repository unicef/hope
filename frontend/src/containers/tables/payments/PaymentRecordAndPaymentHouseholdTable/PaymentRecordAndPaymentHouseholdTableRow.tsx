import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { PaymentRecordAndPaymentNode } from '../../../../__generated__/graphql';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { StatusBox } from '../../../../components/core/StatusBox';
import {
  formatCurrencyWithSymbol,
  paymentRecordStatusToColor,
} from '../../../../utils/utils';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { BlackLink } from '../../../../components/core/BlackLink';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';

interface PaymentRecordAndPaymentTableRowProps {
  paymentRecordOrPayment: PaymentRecordAndPaymentNode;
  openInNewTab: boolean;
  canViewDetails: boolean;
}

export function PaymentRecordAndPaymentHouseholdTableRow({
  paymentRecordOrPayment,
  openInNewTab,
  canViewDetails,
}: PaymentRecordAndPaymentTableRowProps): React.ReactElement {
  const { baseUrl } = useBaseUrl();
  const history = useHistory();
  const paymentRecordDetailsPath = `/${baseUrl}/payment-records/${paymentRecordOrPayment.id}`;
  const paymentDetailsPath = `/${baseUrl}/payment-module/payments/${paymentRecordOrPayment.id}`;
  const detailsPath =
    paymentRecordOrPayment.objType === 'PaymentRecord'
      ? paymentRecordDetailsPath
      : paymentDetailsPath;
  const handleClick = (): void => {
    if (openInNewTab) {
      window.open(detailsPath);
    } else {
      history.push(detailsPath);
    }
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={paymentRecordOrPayment.id}
    >
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={detailsPath}>{paymentRecordOrPayment.caId}</BlackLink>
        ) : (
          paymentRecordOrPayment.caId
        )}
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={paymentRecordOrPayment.status}
          statusToColor={paymentRecordStatusToColor}
        />
      </TableCell>
      <TableCell align='left'>{paymentRecordOrPayment.fullName}</TableCell>
      <TableCell align='left'>
        {paymentRecordOrPayment?.parent?.programmeName}
      </TableCell>
      <TableCell align='right'>
        {formatCurrencyWithSymbol(
          paymentRecordOrPayment.entitlementQuantity,
          paymentRecordOrPayment.currency,
        )}
      </TableCell>
      <TableCell align='right'>
        {formatCurrencyWithSymbol(
          paymentRecordOrPayment.deliveredQuantity,
          paymentRecordOrPayment.currency,
        )}
      </TableCell>
      <TableCell align='right'>
        <UniversalMoment>{paymentRecordOrPayment.deliveryDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
