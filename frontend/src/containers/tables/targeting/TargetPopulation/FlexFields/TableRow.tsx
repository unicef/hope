import TableCell from '@mui/material/TableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';

export function FlexFieldRow() {
  return (
    <ClickableTableRow hover role="checkbox">
      <TableCell align="left">---</TableCell>
      <TableCell align="left">---</TableCell>
    </ClickableTableRow>
  );
}
