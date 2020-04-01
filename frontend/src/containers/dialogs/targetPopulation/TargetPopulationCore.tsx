import React from 'react';
import styled from 'styled-components';
import { TargetPopulationDetails } from '../../../components/TargetPopulation/TargetPopulationDetails';
import { TargetingCriteria } from '../../../components/TargetPopulation/TargetingCriteria';
import { Results } from '../../../components/TargetPopulation/Results';
import { Paper, Typography } from '@material-ui/core';

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

//this data is going to be in targetPopulation prop
const resultsData = {
  totalNumberOfHouseholds: 125,
  targetedIndividuals: 254,
  femaleChildren: 43,
  maleChildren: 50,
  femaleAdults: 35,
  maleAdults: 12,
};

const criterias = [
  {
    intakeGroup: 'Children 9/10/2019',
    sex: 'Female',
    age: '7 - 15 years old',
    distanceToSchool: 'over 3km',
    household: 'over 5 individuals',
    core: [
      {
        label: 'residence_status',
        value: 'MIGRANT',
      },
    ],
  },
  {
    intakeGroup: 'Children 9/10/2019',
    sex: 'Male',
    age: null,
    distanceToSchool: 'over 3km',
    household: null,
    core: [
      {
        label: 'residence_status',
        value: 'CITIZEN',
      },
    ],
  },
];

const candidateLiistTargetingCriteria = {
  rules: [
    {
      id: '122',
      filters: [
        {
          id: '1',
          comparisionMethod: 'NOT_EQUALS',
          isFlexField: false,
          fieldName: 'years_in_school',
          arguments: [5],
        },
        {
          id: '2',
          comparisionMethod: 'RANGE',
          isFlexField: false,
          fieldName: 'family_size',
          arguments: [5, 7],
        },
        {
          id: '3',
          comparisionMethod: 'EQUALS',
          isFlexField: false,
          fieldName: 'residence_status',
          arguments: ['CITIZEN'],
        },
      ],
    },
    {
      id: '12',
      filters: [
        {
          id: '4',
          comparisionMethod: 'NOT_EQUALS',
          isFlexField: false,
          fieldName: 'years_in_school',
          arguments: [5],
        },
        {
          id: '5',
          comparisionMethod: 'RANGE',
          isFlexField: false,
          fieldName: 'family_size',
          arguments: [5, 7],
        },
        {
          id: '6',
          comparisionMethod: 'EQUALS',
          isFlexField: false,
          fieldName: 'residence_status',
          arguments: ['CITIZEN'],
        },
      ],
    },
  ],
};

export function TargetPopulationCore({ targetPopulation }) {
  return (
    <>
      {targetPopulation.status === 'FINALIZED' && (
        <TargetPopulationDetails targetPopulation={targetPopulation} />
      )}
      <TargetingCriteria criterias={candidateLiistTargetingCriteria.rules} />
      <Results resultsData={resultsData} />
      <PaperContainer>
        <Title>
          <Typography variant='h6'>
            Target Population Entries (Households)
          </Typography>
        </Title>
      </PaperContainer>
    </>
  );
}
