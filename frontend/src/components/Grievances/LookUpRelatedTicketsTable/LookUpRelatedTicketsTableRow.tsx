import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import React from 'react';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { Pointer } from '../../Pointer';
import { ClickableTableRow } from '../../table/ClickableTableRow';
import { StatusBox } from '../../StatusBox';
import { cashPlanStatusToColor } from '../../../utils/utils';
import { Missing } from '../../Missing';
import { UniversalMoment } from '../../UniversalMoment';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface LookUpRelatedTicketsTableRowProps {
  ticket;
}

export function LookUpRelatedTicketsTableRow({
  ticket,
}: LookUpRelatedTicketsTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();
  const handleClick = (): void => {
    const path = `/${businessArea}/grievance-and-feedback/${ticket.id}`;
    const win = window.open(path, '_blank rel=noopener');
    if (win != null) {
      win.focus();
    }
  };

  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={ticket.id}
    >
      <TableCell align='left'>{ticket.id}</TableCell>
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
