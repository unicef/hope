import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import React from 'react';
import { useHistory } from 'react-router-dom';
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
      <TableCell align='left'>{`${ticket.assignedTo.firstName} ${ticket.assignedTo.lastName}`}</TableCell>
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
