import React, { ReactElement } from 'react';
import styled from 'styled-components';
import { useCandidateHouseholdsListByTargetingCriteriaQuery} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { ProgrammeTableRow } from '../SentTargeting/ProgrammeTableRow';
import { headCells as programmeHeadCells } from '../SentTargeting/ProgrammeHeadCells';
import { headCells as targetPopulationHeadCells } from '../SentTargeting/TargetPopulationHeadCells';
import { TargetPopulationHouseholdTableRow } from '../SentTargeting/TargetPopulationTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface TargetPopulationHouseholdProps {
  id?: string;
  query?;
  queryObjectName?;
  variables?;
  selectedTab: number;
}

export const ApprovedTargetPopulationTable = ({
  id,
  variables,
  selectedTab,
}: TargetPopulationHouseholdProps): ReactElement => {
  const initialVariables = {
    ...(id && { targetPopulation: id }),
    ...variables,
  };
  return (
    <TableWrapper>
      <UniversalTable
        title='Households'
        headCells={
          selectedTab === 0 ? programmeHeadCells : targetPopulationHeadCells
        }
        rowsPerPageOptions={[10, 15, 20]}
        query={useCandidateHouseholdsListByTargetingCriteriaQuery}
        queriedObjectName='candidateHouseholdsListByTargetingCriteria'
        initialVariables={initialVariables}
        renderRow={(row) => {
          return selectedTab === 0 ? (
            <ProgrammeTableRow household={row} />
          ) : (
            <TargetPopulationHouseholdTableRow household={row} />
          );
        }}
      />
    </TableWrapper>
  );
};
