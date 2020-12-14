import React, { ReactElement } from 'react';
import styled from 'styled-components';
import {
  TargetPopulationNode,
  useAllTargetPopulationsQuery,
  AllTargetPopulationsQueryVariables,
} from '../../../__generated__/graphql';
import { decodeIdString } from '../../../utils/utils';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './TargetPopulationTableHeadCells';
import { TargetPopulationTableRow } from './TargetPopulationTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface TargetPopulationProps {
  filter;
}

export const TargetPopulationTable = ({
  filter,
}: TargetPopulationProps): ReactElement => {
  const businessArea = useBusinessArea();
  const initialVariables: AllTargetPopulationsQueryVariables = {
    name: filter.name,
    candidateListTotalHouseholdsMin: filter.numIndividuals.min,
    candidateListTotalHouseholdsMax: filter.numIndividuals.max,
    status: filter.status,
    businessArea,
  };
  if (filter.program) {
    if (Array.isArray(filter.program)) {
      initialVariables.program = filter.program.map((programId) =>
        decodeIdString(programId),
      );
    } else {
      initialVariables.program = [decodeIdString(filter.program)];
    }
  }
  return (
    <TableWrapper>
      <UniversalTable<TargetPopulationNode, AllTargetPopulationsQueryVariables>
        title='Target Populations'
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllTargetPopulationsQuery}
        queriedObjectName='allTargetPopulation'
        defaultOrderBy='createdAt'
        defaultOrderDirection='desc'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <TargetPopulationTableRow key={row.id} targetPopulation={row} />
        )}
      />
    </TableWrapper>
  );
};
