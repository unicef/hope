import TableCell from '@mui/material/TableCell';
import React from 'react';
import { Checkbox } from '@mui/material';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../core/Table/ClickableTableRow';
import { StatusBox } from '../../../core/StatusBox';
import {
  grievanceTicketStatusToColor,
  renderUserName,
} from '../../../../utils/utils';
import { AllGrievanceTicketQuery } from '../../../../__generated__/graphql';
import { BlackLink } from '../../../core/BlackLink';

interface LookUpRelatedTicketsTableRowProps {
  ticket: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'];
  selected: Array<string>;
  checkboxClickHandler: (
    event:
      | React.MouseEvent<HTMLButtonElement, MouseEvent>
      | React.MouseEvent<HTMLTableRowElement, MouseEvent>,
    number,
  ) => void;
  statusChoices: { [id: number]: string };
  categoryChoices: { [id: number]: string };
}

export function LookUpRelatedTicketsTableRow({
  ticket,
  selected,
  checkboxClickHandler,
  statusChoices,
  categoryChoices,
}: LookUpRelatedTicketsTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();
  const isSelected = (name: string): boolean => selected.includes(name);
  const isItemSelected = isSelected(ticket.id);

  return (
    <ClickableTableRow
      onClick={(event) => checkboxClickHandler(event, ticket.id)}
      hover
      role='checkbox'
      key={ticket.id}
    >
      <TableCell padding='checkbox'>
        <Checkbox
          color='primary'
          onClick={(event) => checkboxClickHandler(event, ticket.id)}
          checked={isItemSelected}
          inputProps={{ 'aria-labelledby': ticket.id }}
        />
      </TableCell>
      <TableCell align='left'>
        <BlackLink to={`/${businessArea}/grievance-and-feedback/${ticket.id}`}>
          {ticket.unicefId}
        </BlackLink>
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={statusChoices[ticket.status]}
          statusToColor={grievanceTicketStatusToColor}
        />
      </TableCell>
      <TableCell align='left'>{categoryChoices[ticket.category]}</TableCell>
      <TableCell align='left'>{ticket.household?.unicefId || '-'}</TableCell>
      <TableCell align='left'>{renderUserName(ticket.assignedTo)}</TableCell>
      <TableCell align='left'>{ticket.admin}</TableCell>
    </ClickableTableRow>
  );
}
