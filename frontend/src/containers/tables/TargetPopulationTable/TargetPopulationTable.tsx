import React, { ReactElement } from 'react';
import styled from 'styled-components';
import {
  TargetPopulationNode,
  useAllTargetPopulationsQuery,
  AllTargetPopulationsQueryVariables,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './TargetPopulationTableHeadCells';
import { TargetPopulationTableRow } from './TargetPopulationTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface TargetPopulationProps {
  businessArea: string;
  sizeFilter: { min: number | undefined; max: number | undefined };
  textFilter: string;
}

export const TargetPopulationTable = ({
  businessArea,
  sizeFilter,
  textFilter
}: TargetPopulationProps): ReactElement => {
  const initialVariables = {
    name: textFilter
  };
  return (
    <TableWrapper>
      <UniversalTable<TargetPopulationNode, AllTargetPopulationsQueryVariables>
        title='Target Population'
        headCells={headCells}
        rowsPage={[10, 15, 20]}
        query={useAllTargetPopulationsQuery}
        queriedObjectName='allTargetPopulation'
        initialVariables={initialVariables}
        renderRow={(row) => <TargetPopulationTableRow targetPopulation={row} />}
      />
    </TableWrapper>
  );
};
