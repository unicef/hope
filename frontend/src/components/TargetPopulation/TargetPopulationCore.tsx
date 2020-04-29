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

//this data is going to be in targetPopulation prop
const resultsData = {
  totalNumberOfHouseholds: 125,
  targetedIndividuals: 254,
  femaleChildren: 43,
  maleChildren: 50,
  femaleAdults: 35,
  maleAdults: 12,
};

export function TargetPopulationCore({
  candidateList,
  targetPopulationList = null,
  id,
  selectedTab = 0,
  status,
  targetPopulation,
}) {
  if (!candidateList) return null;
  const { rules: candidateListRules } = candidateList;
  return (
    <>
      <TargetingCriteria
        selectedTab={selectedTab}
        candidateListRules={candidateListRules}
        targetPopulationRules={targetPopulationList?.rules}
      />
      <Results
        resultsData={resultsData}
        totalNumOfHouseholds={targetPopulation.candidateListTotalHouseholds}
        finalListTotalHouseholds={targetPopulation.finalListTotalHouseholds}
      />
      {candidateListRules.length ? (
        <TargetingHouseholds
          id={id}
          status={status}
          selectedTab={selectedTab}
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
