import TableCell from '@material-ui/core/TableCell';
import TableRow from '@material-ui/core/TableRow';
import React from 'react';

export function EnhancedTableRow({ row, columns, handleClick }): React.ReactElement  {
  return (
    <TableRow
      hover
      onClick={(event) => handleClick(event, row.name.toString())}
      role='checkbox'
      tabIndex={-1}
      key={row.id}
    >
      <TableCell align='right'>{row.name}</TableCell>
      <TableCell align='right'>{row.calories}</TableCell>
      <TableCell align='right'>{row.fat}</TableCell>
      <TableCell align='right'>{row.carbs}</TableCell>
      <TableCell align='right'>{row.protein}</TableCell>
    </TableRow>
  );
}
