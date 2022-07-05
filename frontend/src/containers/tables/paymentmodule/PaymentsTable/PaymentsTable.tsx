import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  hasCreatorOrOwnerPermissions,
  PERMISSIONS,
} from '../../../../config/permissions';
import { UniversalTable } from '../../UniversalTable';
import { usePermissions } from '../../../../hooks/usePermissions';
import { GRIEVANCE_CATEGORIES } from '../../../../utils/constants';
import { decodeIdString, reduceChoices } from '../../../../utils/utils';
import {
  AllGrievanceTicketQueryVariables,
  useGrievancesChoiceDataQuery,
  useMeQuery,
  AllGrievanceTicketQuery,
  useAllGrievanceTicketQuery,
} from '../../../../__generated__/graphql';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { GrievancesTableRow } from '../../../../components/grievances/GrievancesTable/GrievancesTableRow';

import { headCells } from './PaymentsTableHeadCells';
import { PaymentsTableRow } from './PaymentsTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface PaymentsTableProps {
  businessArea: string;
  filter;
}

export const PaymentsTable = ({
  businessArea,
  filter,
}: PaymentsTableProps): React.ReactElement => {
  const { t } = useTranslation();
  const initialVariables: AllGrievanceTicketQueryVariables = {
    businessArea,
    search: filter.search,
    status: [filter.status],
    fsp: filter.fsp,
    createdAtRange: JSON.stringify(filter.createdAtRange),
    admin: [decodeIdString(filter?.admin?.node?.id)],
    registrationDataImport: filter.registrationDataImport,
    category: filter.category,
    assignedTo: filter.assignedTo,
    cashPlan: filter.cashPlan,
  };

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

  return (
    <TableWrapper>
      <UniversalTable<
        AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'],
        AllGrievanceTicketQueryVariables
      >
        headCells={headCells}
        title={t('Payments List')}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllGrievanceTicketQuery}
        queriedObjectName='allGrievanceTicket'
        initialVariables={initialVariables}
        defaultOrderBy='created_at'
        defaultOrderDirection='desc'
        renderRow={(row) => (
          <PaymentsTableRow
            key={row.id}
            ticket={row}
            statusChoices={statusChoices}
            categoryChoices={categoryChoices}
            canViewDetails={getCanViewDetailsOfTicket(row)}
          />
        )}
      />
    </TableWrapper>
  );
};
