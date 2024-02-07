import * as React from 'react';
import TableCell from '@mui/material/TableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';

export function FlexFieldRow({ household }) {
  return (
    <ClickableTableRow hover role="checkbox">
      <TableCell align="left">---</TableCell>
      <TableCell align="left">---</TableCell>
    </ClickableTableRow>
  );
}
