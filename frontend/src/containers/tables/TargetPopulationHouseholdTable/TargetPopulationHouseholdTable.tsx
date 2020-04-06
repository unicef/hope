import React, { ReactElement } from 'react';
import styled from 'styled-components';
import {
  TargetPopulationNode,
  useCandidateHouseholdsListByTargetingCriteriaQuery,
  HouseholdNode,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './TargetPopulationHouseholdHeadCells';
import { TargetPopulationHouseholdTableRow } from './TargetPopulationHouseholdRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface TargetPopulationHouseholdProps {
  id: string;
}

export const TargetPopulationHouseholdTable = ({
  id,
}: TargetPopulationHouseholdProps): ReactElement => {
  const initialVariables = {
    targetPopulation: id,
  };
  return (
    <TableWrapper>
      <UniversalTable
        title='Households'
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useCandidateHouseholdsListByTargetingCriteriaQuery}
        queriedObjectName='candidateHouseholdsListByTargetingCriteria'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <TargetPopulationHouseholdTableRow household={row} />
        )}
      />
    </TableWrapper>
  );
};
