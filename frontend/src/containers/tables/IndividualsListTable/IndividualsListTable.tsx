import React from 'react';
import styled from 'styled-components';
import {
  AllHouseholdsQueryVariables,
  AllIndividualsQueryVariables,
  HouseholdNode,
  IndividualNode,
  useAllIndividualsQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './IndividualsListTableHeadCells';
import { IndividualsListTableRow } from './IndividualsListTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface IndividualsListTableProps {
  ageFilter: { min: number | undefined; max: number | undefined };
  textFilter?: string;
  sexFilter?: string;
  businessArea?: string;
}

export const IndividualsListTable = ({
  ageFilter,
  businessArea,
  sexFilter,
  textFilter,
}: IndividualsListTableProps): React.ReactElement => {
  const initialVariables = {
    age: JSON.stringify(ageFilter),
    businessArea,
    sex: [sexFilter],
    fullNameContains: textFilter,
    // ageGreater: ageFilter.min,
    // ageLower: ageFilter.max
  };

  return (
    <TableWrapper>
      <UniversalTable<IndividualNode, AllIndividualsQueryVariables>
        title='Individuals'
        headCells={headCells}
        rowsPage={[10, 15, 20]}
        query={useAllIndividualsQuery}
        queriedObjectName='allIndividuals'
        initialVariables={initialVariables}
        renderRow={(row) => <IndividualsListTableRow individual={row} />}
      />
    </TableWrapper>
  );
};
