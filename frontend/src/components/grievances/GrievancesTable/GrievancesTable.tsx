import { Box, Button } from '@material-ui/core';
import get from 'lodash/get';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import {
  AllGrievanceTicketQuery,
  AllGrievanceTicketQueryVariables,
  useAllGrievanceTicketQuery,
  useAllUsersForFiltersLazyQuery,
  useGrievancesChoiceDataQuery,
  useMeQuery,
} from '../../../__generated__/graphql';
import {
  PERMISSIONS,
  hasCreatorOrOwnerPermissions,
  hasPermissions,
} from '../../../config/permissions';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_TICKETS_TYPES,
  GRIEVANCE_TICKET_STATES,
} from '../../../utils/constants';
import { choicesToDict } from '../../../utils/utils';
import { LoadingComponent } from '../../core/LoadingComponent';
import { TableWrapper } from '../../core/TableWrapper';
import { BulkAssignModal } from './BulkAssignModal';
import { headCells } from './GrievancesTableHeadCells';
import { GrievancesTableRow } from './GrievancesTableRow';

interface GrievancesTableProps {
  filter;
  selectedTab;
}

export const GrievancesTable = ({
  filter,
  selectedTab,
}: GrievancesTableProps): React.ReactElement => {
  const { baseUrl, businessArea } = useBaseUrl();
  const { t } = useTranslation();
  const initialVariables: AllGrievanceTicketQueryVariables = {
    businessArea,
    search: `${filter.search && filter.searchType} ${filter.search}`,
    status: [filter.status],
    fsp: filter.fsp,
    createdAtRange: JSON.stringify({
      min: filter.createdAtRangeMin,
      max: filter.createdAtRangeMax,
    }),
    category: filter.category,
    issueType: filter.issueType,
    assignedTo: filter.assignedTo,
    admin: filter.admin,
    registrationDataImport: filter.registrationDataImport,
    cashPlan: filter.cashPlan,
    scoreMin: filter.scoreMin,
    scoreMax: filter.scoreMax,
    grievanceType: filter.grievanceType,
    grievanceStatus: filter.grievanceStatus,
    priority: filter.priority,
    urgency: filter.urgency,
    preferredLanguage: filter.preferredLanguage,
    //TODO: add fitler for program
    // program: programId,
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

  const [selected, setSelected] = useState<string[]>([]);

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
    _event:
      | React.MouseEvent<HTMLButtonElement, MouseEvent>
      | React.MouseEvent<HTMLTableRowElement, MouseEvent>,
    name: string,
  ): void => {
    _event.stopPropagation();
    const selectedIndex = selected.indexOf(name);
    const newSelected = [...selected];

    if (selectedIndex === -1) {
      newSelected.push(name);
    } else {
      newSelected.splice(selectedIndex, 1);
    }

    setSelected(newSelected);
  };

  const handleSelectAllCheckboxesClick = (event, rows): void => {
    event.preventDefault();
    if (!selected.length) {
      const newSelecteds = rows
        .filter((row) => row.status !== GRIEVANCE_TICKET_STATES.CLOSED)
        .map((row) => row.unicefId);
      setSelected(newSelecteds);

      return;
    }
    setSelected([]);
  };

  return (
    <>
      <Box display='flex' flexDirection='column' px={5} pt={5}>
        <Box display='flex' justifyContent='space-between' px={5}>
          <BulkAssignModal
            optionsData={optionsData}
            selected={selected}
            businessArea={businessArea}
            initialVariables={initialVariables}
            setInputValue={setInputValue}
            setSelected={setSelected}
          />
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
            {selectedTab === GRIEVANCE_TICKETS_TYPES.userGenerated &&
              hasPermissions(PERMISSIONS.GRIEVANCES_CREATE, permissions) && (
                <Button
                  alignItems='center'
                  variant='contained'
                  color='primary'
                  component={Link}
                  to={`/${baseUrl}/grievance/new-ticket`}
                  data-cy='button-new-ticket'
                >
                  {t('NEW TICKET')}
                </Button>
              )}
          </Box>
        </Box>
        <TableWrapper>
          <UniversalTable<
            AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'],
            AllGrievanceTicketQueryVariables
          >
            headCells={headCells}
            title={t('Grievance Tickets List')}
            rowsPerPageOptions={[10, 15, 20]}
            query={useAllGrievanceTicketQuery}
            onSelectAllClick={handleSelectAllCheckboxesClick}
            numSelected={selected.length}
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
                selected={selected}
                optionsData={optionsData}
                setInputValue={setInputValue}
                initialVariables={initialVariables}
              />
            )}
          />
        </TableWrapper>
      </Box>
    </>
  );
};
