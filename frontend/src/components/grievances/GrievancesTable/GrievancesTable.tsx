import { Box, Button } from '@material-ui/core';
import get from 'lodash/get';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import {
  hasCreatorOrOwnerPermissions,
  hasPermissions,
  PERMISSIONS,
} from '../../../config/permissions';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import { usePermissions } from '../../../hooks/usePermissions';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_TICKETS_TYPES,
  GRIEVANCE_TICKET_STATES,
} from '../../../utils/constants';
import { choicesToDict, dateToIsoString } from '../../../utils/utils';
import {
  AllGrievanceTicketQueryVariables,
  useAllUsersForFiltersLazyQuery,
  useGrievancesChoiceDataQuery,
  useMeQuery,
  AllGrievanceTicketQuery,
  useAllGrievanceTicketQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../core/LoadingComponent';
import { TableWrapper } from '../../core/TableWrapper';
import { BulkAssignModal } from './bulk/BulkAssignModal';
import { headCells } from './GrievancesTableHeadCells';
import { GrievancesTableRow } from './GrievancesTableRow';
import Paper from '@material-ui/core/Paper';
import { EnhancedTableToolbar } from '../../core/Table/EnhancedTableToolbar';

interface GrievancesTableProps {
  businessArea: string;
  filter;
  selectedTab;
}

export const GrievancesTable = ({
  businessArea,
  filter,
  selectedTab,
}: GrievancesTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const initialVariables: AllGrievanceTicketQueryVariables = {
    businessArea,
    search: filter.search.trim(),
    searchType: filter.searchType,
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
  };

  const [inputValue, setInputValue] = useState('');

  const [loadData, { data }] = useAllUsersForFiltersLazyQuery({
    variables: {
      businessArea,
      first: 20,
      orderBy: 'first_name,last_name,email',
      search: inputValue,
    },
  });

  useEffect(() => {
    loadData();
  }, [loadData]);

  const optionsData = get(data, 'allUsers.edges', []);

  const [selectedTickets, setSelectedTickets] = useState<
    AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'][]
  >([]);

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();
  const {
    data: currentUserData,
    loading: currentUserDataLoading,
  } = useMeQuery();
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
    const index = selectedTickets.findIndex(
      (ticketItem) => ticketItem.id === ticket.id,
    );
    const newSelectedTickets = [...selectedTickets];
    if (index === -1) {
      newSelectedTickets.push(ticket);
    } else {
      newSelectedTickets.splice(index, 1);
    }
    setSelectedTickets(newSelectedTickets);
  };

  const handleSelectAllCheckboxesClick = (event, rows): void => {
    if (!selectedTickets.length) {
      const newSelected = rows
        .filter((row) => row.status !== GRIEVANCE_TICKET_STATES.CLOSED)
        .map((row) => row);
      setSelectedTickets(newSelected);
      return;
    }
    setSelectedTickets([]);
  };

  return (
    <>
      <Box display='flex' flexDirection='column' px={5} pt={5}>
        <Box display='flex' justifyContent='space-between' px={5}>
          <Box display='flex' ml='auto'>
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
            <Box display="flex" flexDirection="row" marginX={6} gridGap={16} >
              <BulkAssignModal
                optionsData={optionsData}
                selectedTickets={selectedTickets}
                businessArea={businessArea}
                initialVariables={initialVariables}
                setInputValue={setInputValue}
                setSelected={setSelectedTickets}
              />
              {selectedTab === GRIEVANCE_TICKETS_TYPES.userGenerated &&
                hasPermissions(PERMISSIONS.GRIEVANCES_CREATE, permissions) && (
                  <Button
                    alignItems='center'
                    variant='contained'
                    color='primary'
                    component={Link}
                    to={`/${businessArea}/grievance/new-ticket`}
                    data-cy='button-new-ticket'
                  >
                    {t('NEW TICKET')}
                  </Button>
                )}
            </Box>
            <UniversalTable<
              AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'],
              AllGrievanceTicketQueryVariables
            >
              isOnPaper={false}
              headCells={headCells}
              rowsPerPageOptions={[10, 15, 20, 40]}
              query={useAllGrievanceTicketQuery}
              onSelectAllClick={handleSelectAllCheckboxesClick}
              numSelected={selectedTickets.length}
              queriedObjectName='allGrievanceTicket'
              initialVariables={initialVariables}
              defaultOrderBy='created_at'
              defaultOrderDirection='desc'
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
    </>
  );
};
