import React from 'react';
import styled from 'styled-components';
import { Paper, Typography } from '@material-ui/core';
import { TargetingCriteria } from './TargetingCriteria';
import { Results } from './Results';
import { TargetingHouseholds } from './TargetingHouseholds';

const PaperContainer = styled(Paper)`
  display: flex;
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  flex-direction: column;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const Label = styled.p`
  color: #b1b1b5;
`;

export function TargetPopulationCore({
  candidateList,
  targetPopulationList = null,
  id,
  status,
  targetPopulation,
}): React.ReactElement {
  if (!candidateList) return null;
  const { rules: candidateListRules } = candidateList;
  const totalNumOfHouseholds = targetPopulation.candidateListTotalHouseholds
  const totalNumOfIndividuals = targetPopulation.candidateListTotalIndividuals
  return (
    <>
      <TargetingCriteria
        candidateListRules={candidateListRules}
        targetPopulationRules={targetPopulationList?.rules}
      />
      <Results
        resultsData={targetPopulation.candidateStats}
        totalNumOfHouseholds={totalNumOfHouseholds}
        totalNumOfIndividuals={totalNumOfIndividuals}
      />
      {candidateListRules.length ? (
        <TargetingHouseholds
          id={id}
          status={status}
        />
      ) : (
        <PaperContainer>
          <Typography variant='h6'>
            Target Population Entries (Households)
          </Typography>
          <Label>Add targeting criteria to see results.</Label>
        </PaperContainer>
      )}
    </>
  );
}
