import React, { ReactElement } from 'react';
import styled from 'styled-components';
import {
  TargetPopulationNode,
  useAllTargetPopulationsQuery,
  AllTargetPopulationsQuery,
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
}: TargetPopulationProps): ReactElement => {
  const initialVariables = {
    businessArea,
  };
  return (
    <TableWrapper>
      <UniversalTable<TargetPopulationNode, AllTargetPopulationsQuery>
        title='Target Population'
        headCells={headCells}
        rowsPage={[10, 15, 20]}
        query={useAllTargetPopulationsQuery}
        queriedObjectName='allTargetPopulation'
        initialVariables={null}
        renderRow={(row) => <TargetPopulationTableRow targetPopulation={row} />}
      />
    </TableWrapper>
  );
};
