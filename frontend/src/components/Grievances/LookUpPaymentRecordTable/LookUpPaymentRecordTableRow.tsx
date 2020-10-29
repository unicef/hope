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

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface LookUpPaymentRecordTableRowProps {
  paymentRecord: PaymentRecordNode;
  openInNewTab: boolean;
}

export function LookUpPaymentRecordTableRow({
  paymentRecord,
  openInNewTab,
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
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={paymentRecord.id}
    >
      <TableCell align='left'>{paymentRecord.caId}</TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={paymentRecord.verifications?.edges[0]?.node.status || ''}
            statusToColor={verificationRecordsStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>{paymentRecord.cashPlan.name}</TableCell>
      <TableCell align='right'>{paymentRecord.deliveredQuantity}</TableCell>
      <TableCell align='right'>
        <Missing />
      </TableCell>
    </ClickableTableRow>
  );
}
