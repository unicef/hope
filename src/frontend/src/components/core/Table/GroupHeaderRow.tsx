import { ReactElement } from 'react';
import TableCell from '@mui/material/TableCell';
import TableRow from '@mui/material/TableRow';
import { blue } from '@mui/material/colors';

interface GroupHeaderRowProps {
  name?: string | null;
}

export function GroupHeaderRow({ name }: GroupHeaderRowProps): ReactElement {
  return (
    <TableRow
      data-cy="group-header-row"
      sx={{
        backgroundColor: blue[50],
        borderTop: `3px solid ${blue[200]}`,
        borderBottom: `1px solid ${blue[100]}`,
      }}
    >
      <TableCell
        colSpan={20}
        sx={{
          fontWeight: 700,
          fontSize: '0.95rem',
          color: blue[900],
          py: 1,
          px: 2,
          borderLeft: `4px solid ${blue[400]}`,
          letterSpacing: '0.02em',
        }}
      >
        {name ?? 'No Group'}
      </TableCell>
    </TableRow>
  );
}
