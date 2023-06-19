import { Checkbox } from '@material-ui/core';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useLocation } from 'react-router-dom';
import {
  AllGrievanceTicketDocument,
  AllGrievanceTicketQuery,
  useBulkUpdateGrievanceAssigneeMutation,
} from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { GRIEVANCE_TICKET_STATES } from '../../../utils/constants';
import {
  grievanceTicketBadgeColors,
  grievanceTicketStatusToColor,
  renderUserName,
} from '../../../utils/utils';
import { BlackLink } from '../../core/BlackLink';
import { StatusBox } from '../../core/StatusBox';
import { ClickableTableRow } from '../../core/Table/ClickableTableRow';
import { UniversalMoment } from '../../core/UniversalMoment';
import { LinkedTicketsModal } from '../LinkedTicketsModal/LinkedTicketsModal';
import { AssignedToDropdown } from './AssignedToDropdown';

interface GrievancesTableRowProps {
  ticket: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'];
  statusChoices: { [id: number]: string };
  categoryChoices: { [id: number]: string };
  canViewDetails: boolean;
  issueTypeChoicesData;
  priorityChoicesData;
  urgencyChoicesData;
  checkboxClickHandler: (
    event:
      | React.MouseEvent<HTMLButtonElement, MouseEvent>
      | React.MouseEvent<HTMLTableRowElement, MouseEvent>,
    number,
  ) => void;
  selected: Array<string>;
  optionsData;
  setInputValue;
  initialVariables;
}

export function GrievancesTableRow({
  ticket,
  statusChoices,
  categoryChoices,
  canViewDetails,
  issueTypeChoicesData,
  priorityChoicesData,
  urgencyChoicesData,
  checkboxClickHandler,
  selected,
  optionsData,
  setInputValue,
  initialVariables,
}: GrievancesTableRowProps): React.ReactElement {
  const location = useLocation();
  const { baseUrl, businessArea } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const isUserGenerated = location.pathname.indexOf('user-generated') !== -1;
  const userOrSystem = isUserGenerated ? 'user-generated' : 'system-generated';
  const detailsPath = `/${baseUrl}/grievance-and-feedback/tickets/${userOrSystem}/${ticket.id}`;
  const isSelected = (name: string): boolean => selected.includes(name);
  const isItemSelected = isSelected(ticket.unicefId);
  const issueType = ticket.issueType
    ? issueTypeChoicesData
        .find((el) => el.category === ticket.category.toString())
        .subCategories.find((el) => el.value === ticket.issueType.toString())
        .name
    : '-';

  const [mutate] = useBulkUpdateGrievanceAssigneeMutation();

  const onFilterChange = async (assignee, ids): Promise<void> => {
    if (assignee) {
      try {
        await mutate({
          variables: {
            assignedTo: assignee.node.id,
            businessAreaSlug: businessArea,
            grievanceTicketUnicefIds: ids,
          },
          refetchQueries: () => [
            {
              query: AllGrievanceTicketDocument,
              variables: { ...initialVariables },
            },
          ],
        });
      } catch (e) {
        e.graphQLErrors.map((x) => showMessage(x.message));
      }
    }
  };

  return (
    <ClickableTableRow hover role='checkbox' key={ticket.id}>
      <TableCell align='left' padding='checkbox'>
        <Checkbox
          color='primary'
          onClick={(event) => checkboxClickHandler(event, ticket.unicefId)}
          checked={isItemSelected}
          disabled={ticket.status === GRIEVANCE_TICKET_STATES.CLOSED}
          inputProps={{ 'aria-labelledby': ticket.unicefId }}
        />
      </TableCell>
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
      <TableCell align='left'>
        {ticket.status === GRIEVANCE_TICKET_STATES.CLOSED ? (
          renderUserName(ticket.assignedTo)
        ) : (
          <AssignedToDropdown
            optionsData={optionsData}
            onFilterChange={onFilterChange}
            value={ticket.assignedTo}
            ids={[ticket.unicefId]}
            setInputValue={setInputValue}
            disableClearable
          />
        )}
      </TableCell>
      <TableCell align='left'>{categoryChoices[ticket.category]}</TableCell>
      <TableCell align='left'>{issueType}</TableCell>
      <TableCell align='left'>{ticket.household?.unicefId || '-'}</TableCell>
      <TableCell align='left'>
        <StatusBox
          status={
            priorityChoicesData[
              priorityChoicesData.findIndex(
                (obj) => obj.value === ticket.priority,
              )
            ]?.name || '-'
          }
          statusToColor={grievanceTicketBadgeColors}
        />
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={
            urgencyChoicesData[
              urgencyChoicesData.findIndex(
                (obj) => obj.value === ticket.urgency,
              )
            ]?.name || '-'
          }
          statusToColor={grievanceTicketBadgeColors}
        />
      </TableCell>
      <TableCell align='left'>
        <LinkedTicketsModal
          ticket={ticket}
          categoryChoices={categoryChoices}
          statusChoices={statusChoices}
          issueTypeChoicesData={issueTypeChoicesData}
          canViewDetails={canViewDetails}
          baseUrl={baseUrl}
        />
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{ticket.createdAt}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{ticket.userModified}</UniversalMoment>
      </TableCell>
      <TableCell align='left'>{ticket.totalDays}</TableCell>
    </ClickableTableRow>
  );
}
