import React, { ReactElement } from 'react';
import {
  TargetPopulationNode,
  useAllTargetPopulationsQuery,
  AllTargetPopulationsQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './TargetPopulationTableHeadCells';
import { TargetPopulationTableRow } from './TargetPopulationTableRow';

export function TargetPopulationTable(): ReactElement {
  const initialVariables = {};
  return (
    <UniversalTable<TargetPopulationNode, AllTargetPopulationsQuery>
      title='Payment Records'
      headCells={headCells}
      query={useAllTargetPopulationsQuery}
      queriedObjectName='allTargetPopulation'
      initialVariables={null}
      renderRow={(row) => <TargetPopulationTableRow targetPopulation={row} />}
    />
  );
}
