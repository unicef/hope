import React, { useState } from 'react';
import styled from 'styled-components';
import { Typography, Paper, Button } from '@material-ui/core';
import { Formik, Form, Field, FieldArray } from 'formik';
import { Results } from './Results';
import { TargetingCriteria } from './TargetingCriteria';
import { PageHeader } from '../PageHeader';
import { FormikTextField } from '../../shared/Formik/FormikTextField';

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

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

const resultsData = {
  totalNumberOfHouseholds: 125,
  targetedIndividuals: 254,
  femaleChildren: 43,
  maleChildren: 50,
  femaleAdults: 35,
  maleAdults: 12,
};

interface EditTargetPopulationProps {
    targetPopulation?
    cancelEdit?
}

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

const rules = [
  {
    id: '1',
    comparisionMethod: 'NOT_EQUALS',
    isFlexField: false,
    fieldName: 'years_in_school',
    arguments: [5]
  },
  {
    id: '1',
    comparisionMethod: 'RANGE',
    isFlexField: false,
    fieldName: 'family_size',
    arguments: [5, 7]
  },
  {
    id: '1',
    comparisionMethod: 'EQUALS',
    isFlexField: false,
    fieldName: 'residence_status',
    arguments: ["CITIZEN"]
  },
  {
    id: '1',
    comparisionMethod: 'NOT_EQUALS',
    isFlexField: false,
    fieldName: 'years_in_school',
    arguments: [5, 7]
  }
]

const candidateLiistTargetingCriteria = {
  rules: [
    {
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

export function EditTargetPopulation({ targetPopulation, cancelEdit }: EditTargetPopulationProps) {
  const initialValues = {
    name: targetPopulation?.name || '',
    criterias: candidateLiistTargetingCriteria.rules || [],
  };
  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        console.log(values);
      }}
    >
      {({ submitForm, values }) => (
        <Form>
          <PageHeader
            title={
              <Field
                name='name'
                label='Programme Name'
                type='text'
                fullWidth
                required
                component={FormikTextField}
              />
            }
          >
            <>
              {values.name && (
                <ButtonContainer>
                  <Button variant='outlined' color='primary' onClick={cancelEdit}>
                    Cancel
                  </Button>
                </ButtonContainer>
              )}
              <ButtonContainer>
                <Button
                  variant='contained'
                  color='primary'
                  type='submit'
                  onClick={submitForm}
                  disabled={!values.name}
                >
                  Save
                </Button>
              </ButtonContainer>
            </>
          </PageHeader>
          {/* <FieldArray
            name='criterias'
            render={(arrayHelpers) => (
              <TargetingCriteria
                helpers={arrayHelpers}
                criterias={values.criterias}
                isEdit
              />
            )}
          /> */}
          <Results />
          <PaperContainer>
            <Title>
              <Typography variant='h6'>
                Target Population Entries (Households)
              </Typography>
            </Title>
          </PaperContainer>
        </Form>
      )}
    </Formik>
  );
}
