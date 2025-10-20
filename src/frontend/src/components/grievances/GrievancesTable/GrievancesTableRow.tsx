import { Checkbox } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { BulkUpdateGrievanceTicketsAssignees } from '@restgenerated/models/BulkUpdateGrievanceTicketsAssignees';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import {
  grievanceTicketBadgeColors,
  grievanceTicketStatusToColor,
  renderUserName,
  showApiErrorMessages,
} from '@utils/utils';
import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import { UniversalMoment } from '@core/UniversalMoment';
import LinkedTicketsModal from '../LinkedTicketsModal/LinkedTicketsModal';
import { AssignedToDropdown } from './AssignedToDropdown';
import {
  getGrievanceDetailsPath,
  getIssueTypeToDisplay,
} from '../utils/createGrievanceUtils';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';

interface GrievancesTableRowProps {
  ticket: GrievanceTicketList;
  statusChoices: { [id: number]: string };
  categoryChoices: { [id: number]: string };
  canViewDetails: boolean;
  issueTypeChoicesData;
  priorityChoicesData;
  urgencyChoicesData;
  checkboxClickHandler: (ticket: GrievanceTicketList) => void;
  isSelected: boolean;
  optionsData;
  setInputValue;
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
  isSelected,
  optionsData,
  setInputValue,
}: GrievancesTableRowProps): ReactElement {
  const { baseUrl, businessArea, isAllPrograms, programId } = useBaseUrl();
  const { isSocialDctType } = useProgramContext();
  const navigate = useNavigate();
  const { showMessage } = useSnackbar();
  const detailsPath = getGrievanceDetailsPath(
    ticket.id,
    ticket.category,
    baseUrl,
  );
  const issueTypeToDisplay = getIssueTypeToDisplay(ticket.issueType);

  const queryClient = useQueryClient();

  const { mutateAsync } = useMutation({
    mutationFn: (params: BulkUpdateGrievanceTicketsAssignees) => {
      return RestService.restBusinessAreasGrievanceTicketsBulkUpdateAssigneeCreate(
        {
          businessAreaSlug: businessArea,
          formData: params,
        },
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['businessAreasProgramsGrievanceTickets'],
      });
      queryClient.invalidateQueries({
        queryKey: [
          'businessAreasProgramsGrievanceTickets',
          { program: programId },
        ],
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const onFilterChange = async (assignee, ids): Promise<void> => {
    if (assignee) {
      await mutateAsync({
        assignedTo: assignee.id,
        grievanceTicketIds: ids,
      });
    }
  };

  const handleRowClick = (): void => {
    if (canViewDetails) {
      navigate(detailsPath);
    }
    return null;
  };

  const getMappedPrograms = (): ReactElement => {
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

  const getTargetUnicefId = (_ticket) => {
    return isSocialDctType || isAllPrograms
      ? _ticket?.targetId
      : _ticket?.household?.unicefId;
  };
  const targetId = getTargetUnicefId(ticket);

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
      <TableCell align="left">{issueTypeToDisplay}</TableCell>
      <TableCell align="left">{targetId || '-'}</TableCell>
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
}
