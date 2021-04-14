import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { ClickableTableRow } from '../../../../components/table/ClickableTableRow';

export function FlexFieldRow({ household }) {

  return (
    <ClickableTableRow
      hover
      role='checkbox'
    >
      <TableCell align='left'>---</TableCell>
      <TableCell align='left'>---</TableCell>
    </ClickableTableRow>
  );
}
