import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  hasCreatorOrOwnerPermissions,
  PERMISSIONS,
} from '../../../config/permissions';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import { usePermissions } from '../../../hooks/usePermissions';
import { GRIEVANCE_CATEGORIES } from '../../../utils/constants';
import { decodeIdString, reduceChoices } from '../../../utils/utils';
import {
  AllGrievanceTicketQuery,
  AllGrievanceTicketQueryVariables,
  useAllGrievanceTicketQuery,
  useGrievancesChoiceDataQuery,
  useMeQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../core/LoadingComponent';
import { TableWrapper } from '../../core/TableWrapper';
import { headCells } from './GrievancesTableHeadCells';
import { GrievancesTableRow } from './GrievancesTableRow';

interface GrievancesTableProps {
  businessArea: string;
  filter;
}

export const GrievancesTable = ({
  businessArea,
  filter,
}: GrievancesTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const initialVariables: AllGrievanceTicketQueryVariables = {
    businessArea,
    search: filter.search,
    status: [filter.status],
    fsp: filter.fsp,
    createdAtRange: JSON.stringify(filter.createdAtRange),
    category: filter.category,
    issueType: filter.issueType,
    assignedTo: filter.assignedTo,
    admin: [decodeIdString(filter?.admin?.node?.id)],
    registrationDataImport: filter.registrationDataImport,
    cashPlan: filter.cashPlan,
    scoreMin: filter.scoreMin,
    scoreMax: filter.scoreMax,
    grievanceType: filter.grievanceType,
    grievanceStatus: filter.grievanceStatus,
    priority: filter.priority,
    urgency: filter.urgency,
  };

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
  } = reduceChoices(choicesData.grievanceTicketStatusChoices);

  const categoryChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketCategoryChoices);

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

  const handleCheckboxClick = (event, name): void => {
    const selectedIndex = selected.indexOf(name);
    let newSelected = [];

    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, name);
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1));
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(
        selected.slice(0, selectedIndex),
        selected.slice(selectedIndex + 1),
      );
    }

    setSelected(newSelected);
  };

  const handleSelectAllCheckboxesClick = (event, rows): void => {
    if (!selected.length) {
      const newSelecteds = rows.map((row) => row.unicefId);
      setSelected(newSelecteds);

      return;
    }
    setSelected([]);
  };

  const numSelected = selected.length;

  return (
    <TableWrapper>
      <UniversalTable<
        AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'],
        AllGrievanceTicketQueryVariables
      >
        headCells={headCells}
        title={t('Grievance and Feedback List')}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllGrievanceTicketQuery}
        onSelectAllClick={handleSelectAllCheckboxesClick}
        numSelected={numSelected}
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
          />
        )}
      />
    </TableWrapper>
  );
};
