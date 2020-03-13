import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { Typography, Paper, Button } from '@material-ui/core';
import { TargetPopulationPageHeader } from './headers/TargetPopulationPageHeader';
import { Results } from '../../components/TargetPopulation/Results';
import { TargetingCriteria } from '../../components/TargetPopulation/TargetingCriteria';
import {
  useTargetPopulationQuery,
  TargetPopulationNode,
} from '../../__generated__/graphql';
import { EditTargetPopulation } from '../../components/TargetPopulation/EditTargetPopulation';
import { TargetPopulationDetails } from '../../components/TargetPopulation/TargetPopulationDetails';

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

const criterias = [
  {
    intakeGroup: 'Children 9/10/2019',
    sex: 'Female',
    age: '7 - 15 years old',
    distanceToSchool: 'over 3km',
    household: 'over 5 individuals',
  },
  {
    intakeGroup: 'Children 9/10/2019',
    sex: 'Male',
    age: null,
    distanceToSchool: 'over 3km',
    household: null,
  },
];

const resultsData = {
  totalNumberOfHouseholds: 125,
  targetedIndividuals: 254,
  femaleChildren: 43,
  maleChildren: 50,
  femaleAdults: 35,
  maleAdults: 12,
};

export function TargetPopulationDetailsPage() {
  const { id } = useParams();
  const { data, loading } = useTargetPopulationQuery({
    variables: { id },
  });
  const [isEdit, setEditState] = useState(false);

  if (!data) {
    return null;
  }
  const targetPopulation = data.targetPopulation as TargetPopulationNode;

  return (
    <div>
      {isEdit ? (
        <EditTargetPopulation
          criterias={criterias}
          targetPopulation={targetPopulation}
          cancelEdit={() => setEditState(false)}
        />
      ) : (
        <>
          <TargetPopulationPageHeader
            targetPopulation={targetPopulation}
            isEditMode={isEdit}
            setEditState={setEditState}
          />
          {targetPopulation.status === 'FINALIZED' && (
            <TargetPopulationDetails targetPopulation={targetPopulation} />
          )}
          <TargetingCriteria criterias={criterias} isEdit={isEdit} />
          <Results resultsData={resultsData} />
          <PaperContainer>
            <Title>
              <Typography variant='h6'>
                Target Population Entries (Households)
              </Typography>
            </Title>
          </PaperContainer>
        </>
      )}
    </div>
  );
}
