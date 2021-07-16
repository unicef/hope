import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import React from 'react';
import { Checkbox } from '@material-ui/core';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../table/ClickableTableRow';
import { StatusBox } from '../../StatusBox';
import {
  decodeIdString,
  grievanceTicketStatusToColor,
  renderUserName,
} from '../../../utils/utils';
import { AllGrievanceTicketQuery } from '../../../__generated__/graphql';
import { BlackLink } from '../../BlackLink';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface LookUpRelatedTicketsTableRowProps {
  ticket: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'];
  selected: Array<string>;
  checkboxClickHandler: (
    event: React.MouseEvent<HTMLButtonElement, MouseEvent>,
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
    <ClickableTableRow hover role='checkbox' key={ticket.id}>
      <TableCell padding='checkbox'>
        <Checkbox
          color='primary'
          onClick={(event) => checkboxClickHandler(event, ticket.id)}
          checked={isItemSelected}
          inputProps={{ 'aria-labelledby': ticket.id }}
        />
      </TableCell>
      <TableCell align='left'>
        <BlackLink
          target='_blank'
          rel='noopener noreferrer'
          to={`/${businessArea}/grievance-and-feedback/${ticket.id}`}
        >
          {decodeIdString(ticket.id)}
        </BlackLink>
      </TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={statusChoices[ticket.status]}
            statusToColor={grievanceTicketStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>{categoryChoices[ticket.category]}</TableCell>
      <TableCell align='left'>{ticket.household?.unicefId || '-'}</TableCell>
      <TableCell align='left'>{renderUserName(ticket.assignedTo)}</TableCell>
      <TableCell align='left'>{ticket.admin}</TableCell>
    </ClickableTableRow>
  );
}
