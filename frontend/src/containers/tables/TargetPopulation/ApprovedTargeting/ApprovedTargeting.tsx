import React, { ReactElement } from 'react';
import styled from 'styled-components';
import {
  useCandidateHouseholdsListByTargetingCriteriaQuery,
  useFinalHouseholdsListByTargetingCriteriaQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../UniversalTable';
import { ProgrammeTableRow } from '../SentTargeting/ProgrammeTableRow';
import { headCells as programmeHeadCells } from '../SentTargeting/ProgrammeHeadCells';
import { headCells as targetPopulationHeadCells } from '../SentTargeting/TargetPopulationHeadCells';
import { TargetPopulationHouseholdTableRow } from '../SentTargeting/TargetPopulationTableRow';
import { Warning } from '@material-ui/icons';

const TableWrapper = styled.div`
  padding: 20px;
  position: relative;
`;

const Indicator = styled.div`
  padding: ${({ theme }) => theme.spacing(2)}px;
  border: 1px solid #f57f17;
  color: #f57f17;
  position: absolute;
  top: 0;
  right: 0;
  transform: translate(-32px, 32px);
  background-color: rgba(245, 128, 25, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

interface TargetPopulationHouseholdProps {
  id?: string;
  query?;
  queryObjectName?;
  variables?;
  selectedTab: number;
  hasSameResults?: boolean;
}

export const ApprovedTargetPopulationTable = ({
  id,
  variables,
  selectedTab,
  hasSameResults,
}: TargetPopulationHouseholdProps): ReactElement => {
  const initialVariables = {
    ...(id && { targetPopulation: id }),
    ...variables,
  };
  return (
    <TableWrapper>
      {selectedTab === 0 && (
        <UniversalTable
          title='Households'
          headCells={
            selectedTab === 0 ? programmeHeadCells : targetPopulationHeadCells
          }
          rowsPerPageOptions={[10, 15, 20]}
          query={useCandidateHouseholdsListByTargetingCriteriaQuery}
          queriedObjectName='candidateHouseholdsListByTargetingCriteria'
          initialVariables={initialVariables}
          renderRow={(row) => <ProgrammeTableRow household={row} />}
        />
      )}
      {selectedTab === 1 && (
        <>
          <UniversalTable
            title='Households'
            headCells={targetPopulationHeadCells}
            rowsPerPageOptions={[10, 15, 20]}
            query={useFinalHouseholdsListByTargetingCriteriaQuery}
            queriedObjectName='finalHouseholdsListByTargetingCriteria'
            initialVariables={initialVariables}
            renderRow={(row) => (
              <TargetPopulationHouseholdTableRow household={row} />
            )}
          />
          {/* {hasSameResults && (
            <Indicator>
              <Warning /> Same Results as Programme Population
            </Indicator>
          )} */}
        </>
      )}
    </TableWrapper>
  );
};
