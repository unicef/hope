import type { ReactNode } from 'react';
import type { HeadCell } from '@core/Table/EnhancedTableHead';
import type { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import { BlackLink } from '@core/BlackLink';
import { StatusBox } from '@core/StatusBox';
import { UniversalMoment } from '@core/UniversalMoment';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import {
  grievanceTicketBadgeColors,
  grievanceTicketStatusToColor,
  renderUserName,
} from '@utils/utils';
import LinkedTicketsModal from '../LinkedTicketsModal/LinkedTicketsModal';
import { AssignedToDropdown } from './AssignedToDropdown';
import { getIssueTypeToDisplay } from '../utils/createGrievanceUtils';

/**
 * Every column the grievance ticket list can show. A page picks the ones it wants by listing
 * these ids once: the header and the row cells are both derived from that list, so they cannot
 * drift apart.
 */
export type GrievanceColumnId =
  | 'unicef_id'
  | 'status'
  | 'assignedTo'
  | 'category'
  | 'issueType'
  | 'target'
  | 'priority'
  | 'urgency'
  | 'linkedTickets'
  | 'created_at'
  | 'user_modified'
  | 'total_days'
  | 'programs';

/** What a header needs to shape itself: the programme type decides the target column. */
export interface GrievanceHeadContext {
  isSocialDctType: boolean;
  isAllPrograms: boolean;
  beneficiaryGroup;
}

/** Everything a cell renderer needs, assembled once per row by GrievancesTableRow. */
export interface GrievanceCellContext {
  ticket: GrievanceTicketList;
  statusChoices: { [id: number]: string };
  categoryChoices: { [id: number]: string };
  issueTypeChoicesData;
  priorityChoicesData;
  urgencyChoicesData;
  canViewDetails: boolean;
  detailsPath: string;
  baseUrl: string;
  businessArea: string;
  isAllPrograms: boolean;
  isSocialDctType: boolean;
  optionsData;
  setInputValue;
  onFilterChange: (assignee, ids) => Promise<void>;
}

interface GrievanceColumn {
  /**
   * The head cell's `id` is the sort key sent to the API (run through camelToUnderscore by
   * columnToOrderBy), which is why it does not always match the column id above.
   */
  head:
    | HeadCell<Partial<GrievanceTicketList>>
    | ((ctx: GrievanceHeadContext) => HeadCell<Partial<GrievanceTicketList>>);
  /** The cell's content; GrievancesTableRow supplies the surrounding TableCell. */
  render: (ctx: GrievanceCellContext) => ReactNode;
}

export const GRIEVANCE_COLUMNS: Record<GrievanceColumnId, GrievanceColumn> = {
  unicef_id: {
    head: {
      disablePadding: false,
      label: 'Ticket ID',
      id: 'unicef_id',
      numeric: false,
      dataCy: 'ticket-id',
    },
    render: ({ ticket, canViewDetails, detailsPath }) =>
      canViewDetails ? (
        <BlackLink to={detailsPath}>{ticket.unicefId}</BlackLink>
      ) : (
        ticket.unicefId
      ),
  },
  status: {
    head: {
      disablePadding: false,
      label: 'Status',
      id: 'status',
      numeric: false,
      dataCy: 'status',
    },
    render: ({ ticket, statusChoices }) => (
      <StatusBox
        status={statusChoices[ticket.status ?? '']}
        statusToColor={grievanceTicketStatusToColor}
      />
    ),
  },
  assignedTo: {
    head: {
      disablePadding: false,
      label: 'Assigned to',
      id: 'assigned_to__last_name',
      numeric: false,
      dataCy: 'assignedTo',
    },
    render: ({ ticket, optionsData, setInputValue, onFilterChange }) =>
      ticket.status === GRIEVANCE_TICKET_STATES.CLOSED ? (
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
      ),
  },
  category: {
    head: {
      disablePadding: false,
      label: 'Category',
      id: 'category',
      numeric: false,
      dataCy: 'category',
    },
    render: ({ ticket, categoryChoices }) => categoryChoices[ticket.category],
  },
  issueType: {
    head: {
      disablePadding: false,
      label: 'Issue Type',
      id: 'issueType',
      numeric: false,
      dataCy: 'issueType',
    },
    render: ({ ticket }) => getIssueTypeToDisplay(ticket.issueType),
  },
  target: {
    // The only header that depends on context, and the reason the row used to need an alias map:
    // the two variants sort on different backend fields, so they cannot share one id.
    head: ({ isSocialDctType, isAllPrograms, beneficiaryGroup }) =>
      isSocialDctType || isAllPrograms
        ? {
            disablePadding: false,
            label: 'Target ID',
            id: 'target_unicef_id',
            numeric: false,
            dataCy: 'targetId',
            disableSort: true,
          }
        : {
            disablePadding: false,
            label: `${beneficiaryGroup?.groupLabel ?? 'Household'} ID`,
            id: 'household_unicef_id',
            numeric: false,
            dataCy: 'householdId',
          },
    render: ({ ticket, isSocialDctType, isAllPrograms }) =>
      (isSocialDctType || isAllPrograms
        ? ticket?.targetId
        : ticket?.householdUnicefId) || '-',
  },
  priority: {
    head: {
      disablePadding: false,
      label: 'Priority',
      id: 'priority',
      numeric: false,
      dataCy: 'priority',
    },
    render: ({ ticket, priorityChoicesData }) => (
      <StatusBox
        status={
          priorityChoicesData[
            priorityChoicesData.findIndex((obj) => obj.value === ticket.priority)
          ]?.name || '-'
        }
        statusToColor={grievanceTicketBadgeColors}
      />
    ),
  },
  urgency: {
    head: {
      disablePadding: false,
      label: 'Urgency',
      id: 'urgency',
      numeric: false,
      dataCy: 'urgency',
    },
    render: ({ ticket, urgencyChoicesData }) => (
      <StatusBox
        status={
          urgencyChoicesData[
            urgencyChoicesData.findIndex((obj) => obj.value === ticket.urgency)
          ]?.name || '-'
        }
        statusToColor={grievanceTicketBadgeColors}
      />
    ),
  },
  linkedTickets: {
    head: {
      disablePadding: false,
      label: 'Linked Tickets',
      id: 'linked_tickets',
      numeric: false,
      dataCy: 'linkedTickets',
    },
    render: ({
      ticket,
      categoryChoices,
      statusChoices,
      issueTypeChoicesData,
      canViewDetails,
      baseUrl,
    }) => (
      <LinkedTicketsModal
        ticket={ticket}
        categoryChoices={categoryChoices}
        statusChoices={statusChoices}
        issueTypeChoicesData={issueTypeChoicesData}
        canViewDetails={canViewDetails}
        baseUrl={baseUrl}
      />
    ),
  },
  created_at: {
    head: {
      disablePadding: false,
      label: 'Creation Date',
      id: 'created_at',
      numeric: false,
      dataCy: 'createdAt',
    },
    render: ({ ticket }) => (
      <UniversalMoment>{ticket.createdAt}</UniversalMoment>
    ),
  },
  user_modified: {
    head: {
      disablePadding: false,
      label: 'Last Modified Date',
      id: 'user_modified',
      numeric: false,
      dataCy: 'userModified',
    },
    render: ({ ticket }) => (
      <UniversalMoment>{ticket.userModified}</UniversalMoment>
    ),
  },
  total_days: {
    head: {
      disablePadding: false,
      label: 'Total Days',
      id: 'total_days',
      numeric: false,
      dataCy: 'totalDays',
    },
    render: ({ ticket }) => ticket.totalDays,
  },
  programs: {
    head: {
      disablePadding: false,
      label: 'Programmes',
      id: 'programs',
      numeric: false,
      dataCy: 'programs',
    },
    render: ({ ticket, businessArea }) =>
      ticket.programs?.length ? (
        <div>
          {ticket.programs.map((program) => (
            <BlackLink
              key={program.id}
              to={`/${businessArea}/programs/${program.code}/details/${program.code}`}
            >
              {program.name}
            </BlackLink>
          ))}
        </div>
      ) : (
        <div>-</div>
      ),
  },
};

export const DEFAULT_GRIEVANCE_COLUMNS: GrievanceColumnId[] = [
  'unicef_id',
  'status',
  'assignedTo',
  'category',
  'issueType',
  'target',
  'priority',
  'urgency',
  'linkedTickets',
  'created_at',
  'user_modified',
  'total_days',
];

// My Tasks shows a narrower list: each preset already pins the assignee and the ticket status, so
// those columns carry no information there.
export const MY_TASKS_COLUMNS: GrievanceColumnId[] = [
  'unicef_id',
  'category',
  'issueType',
  'priority',
  'urgency',
  'total_days',
];
