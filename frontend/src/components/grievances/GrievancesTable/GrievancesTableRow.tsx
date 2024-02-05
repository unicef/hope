import { Checkbox } from '@mui/material';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import React from 'react';
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
import { getGrievanceDetailsPath } from '../utils/createGrievanceUtils';
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
    ticket: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'],
  ) => void;
  isSelected: boolean;
  optionsData;
  setInputValue;
  initialVariables;
}

export const GrievancesTableRow = ({
  ticket,
  statusChoices,
  categoryChoices,
  canViewDetails,
  issueTypeChoicesData,
  priorityChoicesData,
  urgencyChoicesData,
  checkboxClickHandler,
  isSelected,
  optionsData,
  setInputValue,
  initialVariables,
}: GrievancesTableRowProps): React.ReactElement => {
  const { baseUrl, businessArea, isAllPrograms } = useBaseUrl();
  const history = useHistory();
  const { showMessage } = useSnackbar();
  const detailsPath = getGrievanceDetailsPath(
    ticket.id,
    ticket.category,
    baseUrl,
  );
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
            grievanceTicketIds: ids,
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

  const handleRowClick = (): void => {
    if (canViewDetails) {
      history.push(detailsPath);
    }
    return null;
  };

  const getMappedPrograms = (): React.ReactElement => {
    if (ticket.programs?.length) {
      return (
        <div>
          {ticket.programs.map((program) => (
            <BlackLink
              key={program.id}
              to={`/${baseUrl}/details/${program.id}`}
            >
              {program.name}
            </BlackLink>
          ))}
        </div>
      );
    }
    return <div>-</div>;
  };

  const mappedPrograms = getMappedPrograms();

  return (
    <ClickableTableRow
      onClick={handleRowClick}
      hover
      role="checkbox"
      key={ticket.id}
    >
      <TableCell align="left" padding="checkbox">
        <Checkbox
          color="primary"
          onClick={(event) => {
            event.stopPropagation();
            checkboxClickHandler(ticket);
          }}
          checked={isSelected}
          disabled={ticket.status === GRIEVANCE_TICKET_STATES.CLOSED}
          inputProps={{ 'aria-labelledby': ticket.unicefId }}
        />
      </TableCell>
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={detailsPath}>{ticket.unicefId}</BlackLink>
        ) : (
          ticket.unicefId
        )}
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={statusChoices[ticket.status]}
          statusToColor={grievanceTicketStatusToColor}
        />
      </TableCell>
      <TableCell align="left">
        {ticket.status === GRIEVANCE_TICKET_STATES.CLOSED ? (
          renderUserName(ticket.assignedTo)
        ) : (
          <AssignedToDropdown
            optionsData={optionsData}
            onFilterChange={onFilterChange}
            value={ticket.assignedTo}
            ids={[ticket.id]}
            setInputValue={setInputValue}
            disableClearable
          />
        )}
      </TableCell>
      <TableCell align="left">{categoryChoices[ticket.category]}</TableCell>
      <TableCell align="left">{issueType}</TableCell>
      <TableCell align="left">{ticket.household?.unicefId || '-'}</TableCell>
      <TableCell align="left">
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
      <TableCell align="left">
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
      <TableCell align="left">
        <LinkedTicketsModal
          ticket={ticket}
          categoryChoices={categoryChoices}
          statusChoices={statusChoices}
          issueTypeChoicesData={issueTypeChoicesData}
          canViewDetails={canViewDetails}
          baseUrl={baseUrl}
        />
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{ticket.createdAt}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{ticket.userModified}</UniversalMoment>
      </TableCell>
      <TableCell align="left">{ticket.totalDays}</TableCell>
      {isAllPrograms && <TableCell align="left">{mappedPrograms}</TableCell>}
    </ClickableTableRow>
  );
};
