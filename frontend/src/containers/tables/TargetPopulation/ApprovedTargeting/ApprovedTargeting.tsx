import React, { ReactElement } from 'react';
import styled from 'styled-components';
import { useCandidateHouseholdsListByTargetingCriteriaQuery } from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { ProgrammeTableRow } from '../SentTargeting/ProgrammeTableRow';
import { headCells as programmeHeadCells } from '../SentTargeting/ProgrammeHeadCells';

const TableWrapper = styled.div`
  padding: 20px;
  position: relative;
`;

interface TargetPopulationHouseholdProps {
  id?: string;
  variables?;
}

export const ApprovedTargetPopulationTable = ({
  id,
  variables,
}: TargetPopulationHouseholdProps): ReactElement => {
  const initialVariables = {
    ...(id && { targetPopulation: id }),
    ...variables,
  };
  return (
    <TableWrapper>
      <UniversalTable
        title='Households'
        headCells={programmeHeadCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useCandidateHouseholdsListByTargetingCriteriaQuery}
        queriedObjectName='candidateHouseholdsListByTargetingCriteria'
        initialVariables={initialVariables}
        renderRow={(row) => <ProgrammeTableRow household={row} />}
      />
    </TableWrapper>
  );
};
