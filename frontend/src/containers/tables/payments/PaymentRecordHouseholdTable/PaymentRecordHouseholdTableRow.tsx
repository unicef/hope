import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { PaymentRecordNode } from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { StatusBox } from '../../../../components/core/StatusBox';
import {
  formatCurrencyWithSymbol,
  paymentRecordStatusToColor,
} from '../../../../utils/utils';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { BlackLink } from '../../../../components/core/BlackLink';

interface PaymentRecordTableRowProps {
  paymentRecord: PaymentRecordNode;
  openInNewTab: boolean;
  canViewDetails: boolean;
}

export function PaymentRecordHouseholdTableRow({
  paymentRecord,
  openInNewTab,
  canViewDetails,
}: PaymentRecordTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();
  const history = useHistory();
  const paymentRecordDetailsPath = `/${businessArea}/payment-records/${paymentRecord.id}`;
  const handleClick = (): void => {
    if (openInNewTab) {
      window.open(paymentRecordDetailsPath);
    } else {
      history.push(paymentRecordDetailsPath);
    }
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={paymentRecord.id}
    >
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={paymentRecordDetailsPath}>
            {paymentRecord.caId}
          </BlackLink>
        ) : (
          paymentRecord.caId
        )}
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={paymentRecord.status}
          statusToColor={paymentRecordStatusToColor}
        />
      </TableCell>
      <TableCell align='left'>{paymentRecord.fullName}</TableCell>
      <TableCell align='left'>{paymentRecord?.parent?.program?.name}</TableCell>
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
