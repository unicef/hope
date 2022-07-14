import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../core/Table/ClickableTableRow';
import { StatusBox } from '../../core/StatusBox';
import {
  grievanceTicketStatusToColor,
  renderUserName,
} from '../../../utils/utils';
import { UniversalMoment } from '../../core/UniversalMoment';
import { AllGrievanceTicketQuery } from '../../../__generated__/graphql';
import { BlackLink } from '../../core/BlackLink';
import { LinkedTicketsModal } from '../LinkedTicketsModal/LinkedTicketsModal';

interface GrievancesTableRowProps {
  ticket: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'];
  statusChoices: { [id: number]: string };
  categoryChoices: { [id: number]: string };
  canViewDetails: boolean;
  issueTypeChoicesData;
}

export function GrievancesTableRow({
  ticket,
  statusChoices,
  categoryChoices,
  canViewDetails,
  issueTypeChoicesData,
}: GrievancesTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const detailsPath = `/${businessArea}/grievance-and-feedback/${ticket.id}`;
  const handleClick = (): void => {
    history.push(detailsPath);
  };

  const issueType = ticket.issueType
    ? issueTypeChoicesData
        .filter((el) => el.category === ticket.category.toString())[0]
        .subCategories.filter(
          (el) => el.value === ticket.issueType.toString(),
        )[0].name
    : '-';
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={ticket.id}
    >
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={detailsPath}>{ticket.unicefId}</BlackLink>
        ) : (
          ticket.unicefId
        )}
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={statusChoices[ticket.status]}
          statusToColor={grievanceTicketStatusToColor}
        />
      </TableCell>
      <TableCell align='left'>{renderUserName(ticket.assignedTo)}</TableCell>
      <TableCell align='left'>{categoryChoices[ticket.category]}</TableCell>
      <TableCell align='left'>{issueType}</TableCell>
      <TableCell align='left'>{ticket.household?.unicefId || '-'}</TableCell>
      <TableCell align='left'>{ticket.priority || '-'}</TableCell>
      <TableCell align='left'>
        <LinkedTicketsModal
          ticket={ticket}
          categoryChoices={categoryChoices}
          statusChoices={statusChoices}
          issueTypeChoicesData={issueTypeChoicesData}
          canViewDetails={canViewDetails}
          businessArea={businessArea}
        />
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
