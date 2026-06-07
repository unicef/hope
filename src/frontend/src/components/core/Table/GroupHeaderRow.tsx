import { ReactElement } from 'react';
import TableCell from '@mui/material/TableCell';
import TableRow from '@mui/material/TableRow';
import { blue } from '@mui/material/colors';
import { BlackLink } from '@core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface GroupHeaderRowProps {
  name?: string | null;
  id?: string | null;
}

export function GroupHeaderRow({ name, id }: GroupHeaderRowProps): ReactElement {
  const { baseUrl } = useBaseUrl();
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
        {id ? (
          <BlackLink
            to={`/${baseUrl}/payment-module/groups/${id}`}
            style={{ color: blue[900], fontWeight: 700 }}
          >
            {name ?? 'No Group'}
          </BlackLink>
        ) : (
          name ?? 'No Group'
        )}
      </TableCell>
    </TableRow>
  );
}
