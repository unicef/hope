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
  businessArea?: string;
}

export const IndividualsListTable = ({
  ageFilter,
  businessArea,
}: IndividualsListTableProps): React.ReactElement => {
  const initialVariables = {
   // todo missing filters !important
    // businessArea,
    //   ageGreater: ageFilter.min,
    //   ageLower: ageFilter.max
  };

  return (
    <TableWrapper>
      <UniversalTable<IndividualNode, AllIndividualsQueryVariables>
        title='Individuals'
        headCells={headCells}
        query={useAllIndividualsQuery}
        queriedObjectName='allIndividuals'
        initialVariables={initialVariables}
        renderRow={(row) => <IndividualsListTableRow individual={row} />}
      />
    </TableWrapper>
  );
};
