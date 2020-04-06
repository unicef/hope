import React from 'react';
import styled from 'styled-components';
import { Paper, Typography } from '@material-ui/core';
import { TargetPopulationDetails } from '../../../components/TargetPopulation/TargetPopulationDetails';
import { TargetingCriteria } from '../../../components/TargetPopulation/TargetingCriteria';
import { Results } from '../../../components/TargetPopulation/Results';
import { TargetPopulationHouseholdTable } from '../../tables/TargetPopulationHouseholdTable';

const PaperContainer = styled(Paper)`
  display: flex;
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  flex-direction: column;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
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

export function TargetPopulationCore({ targetPopulation, id }) {
  if (!targetPopulation) return null;
  const { rules } = targetPopulation;
  return (
    <>
      {targetPopulation.status === 'FINALIZED' && (
        <TargetPopulationDetails targetPopulation={targetPopulation} />
      )}
      <TargetingCriteria criterias={rules} />
      <Results resultsData={resultsData} />

      {rules.length ? (
        <TargetPopulationHouseholdTable id={id} />
      ) : (
        <PaperContainer>
          <Title>
            <Typography variant='h6'>
              Target Population Entries (Households)
            </Typography>
            <Label>Add targeting criteria to see results.</Label>
          </Title>
        </PaperContainer>
      )}
    </>
  );
}
