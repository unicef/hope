import React from 'react';
import styled from 'styled-components';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import {
  AllIndividualsQueryVariables,
  IndividualNode,
  useAllIndividualsQuery,
} from '../../../__generated__/graphql';
import { headCells } from './LookUpIndividualTableHeadCells';
import { LookUpIndividualTableRow } from './LookUpIndividualTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface LookUpIndividualTableProps {
  filter;
  businessArea?: string;
}

export const LookUpIndividualTable = ({
  businessArea,
  filter,
}: LookUpIndividualTableProps): React.ReactElement => {
  const initialVariables = {
    age: JSON.stringify(filter.age),
    businessArea,
    sex: [filter.sex],
    search: filter.text,
  };

  return (
    <TableWrapper>
      <UniversalTable<IndividualNode, AllIndividualsQueryVariables>
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllIndividualsQuery}
        queriedObjectName='allIndividuals'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <LookUpIndividualTableRow key={row.id} individual={row} />
        )}
      />
    </TableWrapper>
  );
};
