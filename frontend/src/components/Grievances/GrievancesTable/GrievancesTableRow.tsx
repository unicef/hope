import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { Pointer } from '../../Pointer';
import { ClickableTableRow } from '../../table/ClickableTableRow';
import { StatusBox } from '../../StatusBox';
import { cashPlanStatusToColor, decodeIdString } from '../../../utils/utils';
import { Missing } from '../../Missing';
import { UniversalMoment } from '../../UniversalMoment';
import {
  AllGrievanceTicketQuery,
  GrievancesChoiceDataQuery,
} from '../../../__generated__/graphql';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface GrievancesTableRowProps {
  ticket: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'];
  statusChoices: { [id: number]: string };
}

export function GrievancesTableRow({
  ticket,
  statusChoices,
}: GrievancesTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/grievance-and-feedback/${ticket.id}`;
    history.push(path);
  };
  console.log('ticket', ticket);
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={ticket.id}
    >
      <TableCell align='left'>{decodeIdString(ticket.id)}</TableCell>
      <TableCell align='left'>
        <StatusContainer>
          <StatusBox
            status={statusChoices[ticket.status]}
            statusToColor={cashPlanStatusToColor}
          />
        </StatusContainer>
      </TableCell>
      <TableCell align='left'>
        {ticket.assignedTo.firstName
          ? `${ticket.assignedTo.firstName} ${ticket.assignedTo.lastName}`
          : ticket.assignedTo.email}
      </TableCell>
      <TableCell align='left'>{ticket.category}</TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{ticket.createdAt}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{ticket.userModified}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
