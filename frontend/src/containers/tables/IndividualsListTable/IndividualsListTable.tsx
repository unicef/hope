import React from 'react';
import styled from 'styled-components';
import {
  AllIndividualsQueryVariables,
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
  filter
  businessArea?: string;
}

export const IndividualsListTable = ({
  businessArea,
  filter,
}: IndividualsListTableProps): React.ReactElement => {
  const initialVariables = {
    age: JSON.stringify(filter.age),
    businessArea,
    sex: [filter.sex],
    fullNameContains: filter.text,
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
