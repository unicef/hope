import TableCell from '@mui/material/TableCell';
import { Checkbox } from '@mui/material';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import { StatusBox } from '@core/StatusBox';
import { grievanceTicketStatusToColor, renderUserName } from '@utils/utils';
import { BlackLink } from '@core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { getGrievanceDetailsPath } from '@components/grievances/utils/createGrievanceUtils';
import { MouseEvent, ReactElement } from 'react';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';

interface LookUpLinkedTicketsTableRowProps {
  ticket: GrievanceTicketList;
  selected: Array<string>;
  checkboxClickHandler: (
    event: MouseEvent<HTMLTableRowElement> | MouseEvent<HTMLButtonElement>,
    number,
  ) => void;
  statusChoices: { [id: number]: string };
  categoryChoices: { [id: number]: string };
}

export function LookUpLinkedTicketsTableRow({
  ticket,
  selected,
  checkboxClickHandler,
  statusChoices,
  categoryChoices,
}: LookUpLinkedTicketsTableRowProps): ReactElement {
  const { baseUrl } = useBaseUrl();
  const isSelected = (name: string): boolean => selected.includes(name);
  const isItemSelected = isSelected(ticket.id);
  const grievanceDetailsPath = getGrievanceDetailsPath(
    ticket.id,
    ticket.category,
    baseUrl,
  );

  return (
    <ClickableTableRow
      onClick={(event) => checkboxClickHandler(event, ticket.id)}
      hover
      role="checkbox"
      key={ticket.id}
    >
      <TableCell padding="checkbox">
        <Checkbox
          color="primary"
          onClick={(event) => checkboxClickHandler(event, ticket.id)}
          checked={isItemSelected}
          inputProps={{ 'aria-labelledby': ticket.id }}
        />
      </TableCell>
      <TableCell align="left">
        <BlackLink to={grievanceDetailsPath}>{ticket.unicefId}</BlackLink>
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={statusChoices[ticket.status]}
          statusToColor={grievanceTicketStatusToColor}
        />
      </TableCell>
      <TableCell align="left">{categoryChoices[ticket.category]}</TableCell>
      <TableCell align="left">{ticket.household?.unicefId || '-'}</TableCell>
      <TableCell align="left">{renderUserName(ticket.assignedTo)}</TableCell>
      <TableCell align="left">{ticket.admin}</TableCell>
    </ClickableTableRow>
  );
}
