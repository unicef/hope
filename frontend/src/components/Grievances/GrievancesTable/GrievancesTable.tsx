import React from 'react';
import styled from 'styled-components';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import {
  AllGrievanceTicketQuery,
  AllGrievanceTicketQueryVariables,
  GrievanceTicketNode,
  useAllGrievanceTicketQuery,
  useGrievancesChoiceDataQuery,
} from '../../../__generated__/graphql';
import { headCells } from './GrievancesTableHeadCells';
import { GrievancesTableRow } from './GrievancesTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface GrievancesTableProps {
  businessArea: string;
  filter;
}

export const GrievancesTable = ({
  businessArea,
  filter,
}: GrievancesTableProps): React.ReactElement => {
  const initialVariables: AllGrievanceTicketQueryVariables = {
    businessArea,
    search: filter.search,
    status: [filter.status],
    fsp: [filter.fsp],
    createdAtRange: JSON.stringify(filter.createdAtRange),
    admin: [filter.admin],
  };

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();
  if (choicesLoading) {
    return null;
  }
  const statusChoices: {
    [id: number]: string;
  } = choicesData.grievanceTicketStatusChoices.reduce(
    (previousValue, currentValue) => {
      // eslint-disable-next-line no-param-reassign
      previousValue[currentValue.value] = currentValue.name;
      return previousValue;
    },
    {},
  );
  return (
    <TableWrapper>
      <UniversalTable<AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'], AllGrievanceTicketQueryVariables>
        headCells={headCells}
        title='Grievance and Feedback List'
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllGrievanceTicketQuery}
        queriedObjectName='allGrievanceTicket'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <GrievancesTableRow key={row.id} ticket={row} statusChoices={statusChoices} />
        )}
      />
    </TableWrapper>
  );
};
