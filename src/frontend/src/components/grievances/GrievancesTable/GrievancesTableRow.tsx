import { Checkbox } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import type { BulkUpdateGrievanceTicketsAssignees } from '@restgenerated/models/BulkUpdateGrievanceTicketsAssignees';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import type { ApiErrorShape } from '@utils/utils';
import { showApiErrorMessages } from '@utils/utils';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import { getGrievanceDetailsPath } from '../utils/createGrievanceUtils';
import { useProgramContext } from 'src/programContext';
import type { ReactElement } from 'react';
import type { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import type {
  GrievanceCellContext,
  GrievanceColumnId,
} from './GrievancesTableColumns';
import { GRIEVANCE_COLUMNS } from './GrievancesTableColumns';

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
  /** Columns to render, in order. The header is built from the same list. */
  columns: GrievanceColumnId[];
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
  columns,
}: GrievancesTableRowProps): ReactElement {
  const { baseUrl, businessArea, isAllPrograms } = useBaseUrl();
  const { isSocialDctType } = useProgramContext();
  const navigate = useNavigate();
  const { showMessage } = useSnackbar();
  const detailsPath = getGrievanceDetailsPath(
    ticket.id,
    ticket.category,
    baseUrl,
    ticket.issueType,
  );

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
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsGrievanceTicketsList,
        ),
      });
    },
    onError: (error: ApiErrorShape) => {
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

  const cellContext: GrievanceCellContext = {
    ticket,
    statusChoices,
    categoryChoices,
    issueTypeChoicesData,
    priorityChoicesData,
    urgencyChoicesData,
    canViewDetails,
    detailsPath,
    baseUrl,
    businessArea,
    isAllPrograms,
    isSocialDctType,
    optionsData,
    setInputValue,
    onFilterChange,
  };

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
          slotProps={{ input: { 'aria-labelledby': ticket.unicefId } }}
        />
      </TableCell>
      {columns.map((id) => (
        <TableCell key={id} align="left">
          {GRIEVANCE_COLUMNS[id].render(cellContext)}
        </TableCell>
      ))}
    </ClickableTableRow>
  );
}
