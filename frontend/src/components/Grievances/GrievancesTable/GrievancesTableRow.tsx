import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { Pointer } from '../../Pointer';
import { ClickableTableRow } from '../../table/ClickableTableRow';

interface GrievancesTableRowProps {
  ticket;
}

export function GrievancesTableRow({
  ticket,
}: GrievancesTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/grievance-and-feedback/${ticket.id}`;
    history.push(path);
  };

  return (
    <ClickableTableRow
      onClick={() => handleClick()}
      hover
      role='checkbox'
      key={ticket.id}
    >
      <TableCell align='left'>
        <Pointer>{ticket.id}</Pointer>
      </TableCell>
    </ClickableTableRow>
  );
}
