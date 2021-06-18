import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { Link } from 'react-router-dom';
import { Checkbox } from '@material-ui/core';
import { PaymentRecordNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  formatCurrencyWithSymbol,
  verificationRecordsStatusToColor,
} from '../../../utils/utils';
import { ClickableTableRow } from '../../table/ClickableTableRow';
import { StatusBox } from '../../StatusBox';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface LookUpPaymentRecordTableRowProps {
  paymentRecord: PaymentRecordNode;
  openInNewTab: boolean;
  selected: Array<string>;
  checkboxClickHandler: (
    event: React.MouseEvent<HTMLButtonElement, MouseEvent>,
    number,
  ) => void;
}

export function LookUpPaymentRecordTableRow({
  paymentRecord,
  selected,
  checkboxClickHandler,
}: LookUpPaymentRecordTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();
  const isSelected = (name: string): boolean => selected.includes(name);
  const isItemSelected = isSelected(paymentRecord.id);
  const received =
    paymentRecord?.verifications?.edges?.[0]?.node?.receivedAmount;
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
      <TableCell align='left'>
        <Link
          target='_blank'
          rel='noopener noreferrer'
          to={`/${businessArea}/payment-records/${paymentRecord.id}`}
        >
          {paymentRecord.caId}
        </Link>
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
