import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import React from 'react';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { Pointer } from '../../Pointer';
import { ClickableTableRow } from '../../table/ClickableTableRow';
import { StatusBox } from '../../StatusBox';
import { cashPlanStatusToColor } from '../../../utils/utils';
import { Missing } from '../../Missing';
import { Checkbox } from '@material-ui/core';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface LookUpRelatedTicketsTableRowProps {
  ticket;
  selected: Array<string>;
  checkboxClickHandler;
}

export function LookUpRelatedTicketsTableRow({
  ticket,
  selected,
  checkboxClickHandler,
}: LookUpRelatedTicketsTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();
  const handleClick = (): void => {
    const path = `/${businessArea}/grievance-and-feedback/${ticket.id}`;
    const win = window.open(path, '_blank rel=noopener');
    if (win != null) {
      win.focus();
    }
  };
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
      <TableCell onClick={handleClick} align='left'>
        <Pointer>{ticket.id}</Pointer>
      </TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={ticket.status}
            statusToColor={cashPlanStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>{ticket.category}</TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>{`${ticket.assignedTo.firstName} ${ticket.assignedTo.lastName}`}</TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
    </ClickableTableRow>
  );
}
