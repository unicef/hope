import React, { ReactElement } from 'react';
import styled from 'styled-components';
import { useFinalHouseholdsListByTargetingCriteriaQuery } from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { ProgrammeTableRow } from './ProgrammeTableRow';
import { headCells as programmeHeadCells } from './ProgrammeHeadCells';
import { headCells as targetPopulationHeadCells } from './TargetPopulationHeadCells';
import { TargetPopulationHouseholdTableRow } from './TargetPopulationTableRow';

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

export const SentTargetPopulationTable = ({
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
        query={useFinalHouseholdsListByTargetingCriteriaQuery}
        queriedObjectName='finalHouseholdsListByTargetingCriteria'
        initialVariables={initialVariables}
        renderRow={(row) => {
          return selectedTab === 0 ? (
            <ProgrammeTableRow key={row.name} household={row} />
          ) : (
            <TargetPopulationHouseholdTableRow key={row.name} household={row} />
          );
        }}
      />
    </TableWrapper>
  );
};
