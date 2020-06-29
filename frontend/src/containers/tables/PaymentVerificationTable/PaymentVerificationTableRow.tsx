import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import { HouseholdNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/table/ClickableTableRow';
import { decodeIdString } from '../../../utils/utils';

interface PaymentVerificationTableRowProps {
  plan: HouseholdNode;
}

export function PaymentVerificationTableRow({ plan }) {
  const history = useHistory();
  const businessArea = useBusinessArea();

  // const handleClick = (): void => {
  //   const path = `/${businessArea}/population/household/${household.id}`;
  //   // const win = window.open(path, '_blank');
  //   // if (win != null) {
  //   //   win.focus();
  //   // }
  // };
  return (
    <ClickableTableRow
      hover
      // onClick={handleClick}
      role='checkbox'
      // key={household.id}
    >
      <TableCell align='left'>Cash plan id</TableCell>
      <TableCell align='left'>verification status</TableCell>
      <TableCell align='left'>fsp</TableCell>
      <TableCell align='left'>modality</TableCell>
      <TableCell align='left'>cash amount</TableCell>
      <TableCell align='left'>timeframe</TableCell>
      <TableCell align='left'>programme</TableCell>
    </ClickableTableRow>
  );
}
