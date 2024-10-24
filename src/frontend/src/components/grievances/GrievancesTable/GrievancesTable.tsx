import { UniversalTable } from '@containers/tables/UniversalTable';
import { LoadingComponent } from '@core/LoadingComponent';
import { EnhancedTableToolbar } from '@core/Table/EnhancedTableToolbar';
import { TableWrapper } from '@core/TableWrapper';
import {
  AllGrievanceTicketQuery,
  AllGrievanceTicketQueryVariables,
  useAllGrievanceTicketQuery,
  useAllUsersForFiltersLazyQuery,
  useGrievancesChoiceDataQuery,
  useMeQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useDebounce } from '@hooks/useDebounce';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import Paper from '@mui/material/Paper';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_TICKET_STATES,
} from '@utils/constants';
import { choicesToDict, dateToIsoString } from '@utils/utils';
import get from 'lodash/get';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  PERMISSIONS,
  hasCreatorOrOwnerPermissions,
} from '../../../config/permissions';
import { headCells } from './GrievancesTableHeadCells';
import { GrievancesTableRow } from './GrievancesTableRow';
import { BulkAddNoteModal } from './bulk/BulkAddNoteModal';
import { BulkAssignModal } from './bulk/BulkAssignModal';
import { BulkSetPriorityModal } from './bulk/BulkSetPriorityModal';
import { BulkSetUrgencyModal } from './bulk/BulkSetUrgencyModal';

interface GrievancesTableProps {
  filter;
  selectedTab;
}

export const GrievancesTable = ({
  filter,
}: GrievancesTableProps): React.ReactElement => {
  const { businessArea, programId, isAllPrograms } = useBaseUrl();
  const { t } = useTranslation();

  const initialVariables: AllGrievanceTicketQueryVariables = {
    businessArea,
    search: filter.search.trim(),
    documentType: filter.documentType,
    documentNumber: filter.documentNumber.trim(),
    status: [filter.status],
    fsp: filter.fsp,
    createdAtRange: JSON.stringify({
      min: dateToIsoString(filter.createdAtRangeMin, 'startOfDay'),
      max: dateToIsoString(filter.createdAtRangeMax, 'endOfDay'),
    }),
    category: filter.category,
    issueType: filter.issueType,
    assignedTo: filter.assignedTo,
    createdBy: filter.createdBy,
    admin1: filter.admin1,
    admin2: filter.admin2,
    registrationDataImport: filter.registrationDataImport,
    cashPlan: filter.cashPlan,
    scoreMin: filter.scoreMin,
    scoreMax: filter.scoreMax,
    grievanceType: filter.grievanceType,
    grievanceStatus: filter.grievanceStatus,
    priority: filter.priority === 'Not Set' ? 0 : filter.priority,
    urgency: filter.urgency === 'Not Set' ? 0 : filter.urgency,
    preferredLanguage: filter.preferredLanguage,
    program: isAllPrograms ? filter.program : programId,
    isActiveProgram: filter.programState === 'active' ? true : null,
    isCrossArea: filter.areaScope === 'cross-area' ? true : null,
  };

  const [inputValue, setInputValue] = useState('');
  const debouncedInputText = useDebounce(inputValue, 800);
  const [page, setPage] = useState<number>(0);
  const [loadData, { data }] = useAllUsersForFiltersLazyQuery({
    variables: {
      businessArea,
      first: 20,
      orderBy: 'first_name,last_name,email',
      search: debouncedInputText,
    },
    fetchPolicy: 'cache-and-network',
  });

  useEffect(() => {
    loadData();
  }, [loadData]);

  const optionsData = get(data, 'allUsers.edges', []);

  const [selectedTicketsPerPage, setSelectedTicketsPerPage] = useState<{
    [
      key: number
    ]: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'][];
  }>({ 0: [] });

  const selectedTickets: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'][] =
    [];
  const currentSelectedTickets = selectedTicketsPerPage[page];
  for (const pageKey of Object.keys(selectedTicketsPerPage)) {
    selectedTickets.push(...selectedTicketsPerPage[pageKey]);
  }

  const setSelectedTickets = (
    tickets: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'][],
  ): void => {
    const newSelectedTicketsPerPage = { ...selectedTicketsPerPage };
    newSelectedTicketsPerPage[page] = tickets;
    setSelectedTicketsPerPage(newSelectedTicketsPerPage);
  };

  const { data: choicesData, loading: choicesLoading } =
    useGrievancesChoiceDataQuery();
  const { data: currentUserData, loading: currentUserDataLoading } =
    useMeQuery();
  const permissions = usePermissions();

  if (choicesLoading || currentUserDataLoading) return <LoadingComponent />;
  if (!choicesData || !currentUserData || permissions === null) return null;

  const statusChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.grievanceTicketStatusChoices);

  const categoryChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.grievanceTicketCategoryChoices);

  const issueTypeChoicesData = choicesData.grievanceTicketIssueTypeChoices;
  const priorityChoicesData = choicesData.grievanceTicketPriorityChoices;
  const urgencyChoicesData = choicesData.grievanceTicketUrgencyChoices;
  const currentUserId = currentUserData.me.id;

  const getCanViewDetailsOfTicket = (
    ticket: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'],
  ): boolean => {
    const isTicketCreator = currentUserId === ticket.createdBy?.id;
    const isTicketOwner = currentUserId === ticket.assignedTo?.id;
    if (
      ticket.category.toString() === GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE
    ) {
      return hasCreatorOrOwnerPermissions(
        PERMISSIONS.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
        isTicketCreator,
        PERMISSIONS.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
        isTicketOwner,
        PERMISSIONS.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
        permissions,
      );
    }
    return hasCreatorOrOwnerPermissions(
      PERMISSIONS.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
      isTicketCreator,
      PERMISSIONS.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
      isTicketOwner,
      PERMISSIONS.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
      permissions,
    );
  };

  const handleCheckboxClick = (
    ticket: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'],
  ): void => {
    const index =
      currentSelectedTickets?.findIndex(
        (ticketItem) => ticketItem.id === ticket.id,
      ) ?? -1;

    const newSelectedTickets = [...(currentSelectedTickets || [])];
    if (index === -1) {
      newSelectedTickets.push(ticket);
    } else if (index === 0) {
      newSelectedTickets.shift();
    } else {
      newSelectedTickets.splice(index, 1);
    }
    setSelectedTickets(newSelectedTickets);
  };

  const handleSelectAllCheckboxesClick = (event, rows): void => {
    if (!currentSelectedTickets?.length) {
      const newSelected = rows
        .filter((row) => row.status !== GRIEVANCE_TICKET_STATES.CLOSED)
        .map((row) => row);
      setSelectedTickets(newSelected);
      return;
    }
    setSelectedTickets([]);
  };

  const headCellsWithProgramColumn = [
    ...headCells,
    {
      disablePadding: false,
      label: 'Programmes',
      id: 'programs',
      numeric: false,
      dataCy: 'programs',
    },
  ];

  return (
    <Box display="flex" flexDirection="column" px={5} pt={5}>
      <Box display="flex" justifyContent="space-between" px={5}>
        <Box display="flex" ml="auto">
          <Box>
            {/* TODO: Enable Export Report button */}
            {/* <Button
              startIcon={<GetAppOutlined />}
              variant='text'
              color='primary'
              onClick={() => {
                '';
              }}
            >
              {t('Export Report')}
            </Button> */}
          </Box>
          <Box ml={5} mr={7}>
            {/* TODO: Enable Upload Tickets button */}
            {/* <Button
              startIcon={<PublishOutlined />}
              variant='text'
              color='primary'
              onClick={() => {
                '';
              }}
            >
              {t('Upload Tickets')}
            </Button> */}
          </Box>
        </Box>
      </Box>
      <TableWrapper>
        <Paper>
          <EnhancedTableToolbar title={t('Grievance Tickets List')} />
          <Box
            display="flex"
            flexDirection="row"
            marginX={6}
            gap={4}
            component="div"
          >
            {' '}
            <BulkAssignModal
              selectedTickets={selectedTickets}
              businessArea={businessArea}
              setSelected={setSelectedTickets}
            />
            <BulkSetPriorityModal
              selectedTickets={selectedTickets}
              businessArea={businessArea}
              setSelected={setSelectedTickets}
            />
            <BulkSetUrgencyModal
              selectedTickets={selectedTickets}
              businessArea={businessArea}
              setSelected={setSelectedTickets}
            />
            <BulkAddNoteModal
              selectedTickets={selectedTickets}
              businessArea={businessArea}
              setSelected={setSelectedTickets}
            />
          </Box>
          <UniversalTable<
            AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'],
            AllGrievanceTicketQueryVariables
          >
            isOnPaper={false}
            headCells={isAllPrograms ? headCellsWithProgramColumn : headCells}
            rowsPerPageOptions={[10, 15, 20, 40]}
            query={useAllGrievanceTicketQuery}
            onSelectAllClick={handleSelectAllCheckboxesClick}
            numSelected={currentSelectedTickets?.length || 0}
            queriedObjectName="allGrievanceTicket"
            initialVariables={initialVariables}
            defaultOrderBy="created_at"
            defaultOrderDirection="desc"
            onPageChanged={setPage}
            renderRow={(row) => (
              <GrievancesTableRow
                key={row.id}
                ticket={row}
                statusChoices={statusChoices}
                categoryChoices={categoryChoices}
                issueTypeChoicesData={issueTypeChoicesData}
                priorityChoicesData={priorityChoicesData}
                urgencyChoicesData={urgencyChoicesData}
                canViewDetails={getCanViewDetailsOfTicket(row)}
                checkboxClickHandler={handleCheckboxClick}
                isSelected={Boolean(
                  selectedTickets.find((ticket) => ticket.id === row.id),
                )}
                optionsData={optionsData}
                setInputValue={setInputValue}
                initialVariables={initialVariables}
              />
            )}
          />
        </Paper>
      </TableWrapper>
    </Box>
  );
};
