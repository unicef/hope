import React, { useState } from 'react';
import styled from 'styled-components';
import { Typography, Paper, Button, Tabs, Tab } from '@material-ui/core';
import { Formik, Form, Field, FieldArray } from 'formik';
import { Results } from './Results';
import { TargetingCriteria } from './TargetingCriteria';
import { PageHeader } from '../PageHeader';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { BreadCrumbsItem } from '../BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { TargetPopulationHouseholdTable } from '../../containers/tables/TargetPopulationHouseholdTable';
import {
  useGoldenRecordByTargetingCriteriaQuery,
  useUpdateTpMutation
} from '../../__generated__/graphql';
import { useSnackbar } from '../../hooks/useSnackBar';

const PaperContainer = styled(Paper)`
  display: flex;
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  flex-direction: column;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

const Label = styled.p`
  color: #b1b1b5;
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
  id?;
  targetPopulationCriterias?;
  targetPopulationName?;
  cancelEdit?;
}

export function EditTargetPopulation({
  id,
  targetPopulationName,
  targetPopulationCriterias,
  cancelEdit,
}: EditTargetPopulationProps) {
  const initialValues = {
    name: targetPopulationName || '',
    criterias: targetPopulationCriterias.rules || [],
  };
  const [mutate] = useUpdateTpMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Targeting',
      to: `/${businessArea}/target-population/`,
    },
  ];
  const tabs = (
    <Tabs
      value={0}
      aria-label='tabs'
      indicatorColor='primary'
      textColor='primary'
    >
      <Tab label='Candidate list' />
      <Tab label='Target Population' disabled />
    </Tabs>
  );
  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        const { data } = await mutate({
          variables: {
            input: {
              id,
              name: values.name,
              targetingCriteria: {
                rules: values.criterias.map((rule) => {
                  return {
                    ...rule,
                    filters: rule.filters.map((each) => {
                      return {
                        comparisionMethod: each.comparisionMethod,
                        arguments: each.arguments,
                        fieldName: each.fieldName,
                        isFlexField: each.isFlexField,
                      };
                    }),
                  };
                }),
              },
            },
          },
        });
        cancelEdit();
        showMessage('Target Population Updated', {
          pathname: `/${businessArea}/target-population/${id}`,
          historyMethod: 'push',
        });
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
            tabs={tabs}
            breadCrumbs={breadCrumbsItems}
            hasInputComponent
          >
            <>
              {values.name && (
                <ButtonContainer>
                  <Button
                    variant='outlined'
                    color='primary'
                    onClick={cancelEdit}
                  >
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
          <FieldArray
            name='criterias'
            render={(arrayHelpers) => (
              <TargetingCriteria
                helpers={arrayHelpers}
                criterias={values.criterias}
                isEdit
              />
            )}
          />
          <Results />
          {values.criterias.length ? (
            <TargetPopulationHouseholdTable
              variables={{
                targetingCriteria: {
                  rules: values.criterias.map((rule) => {
                    return {
                      filters: rule.filters.map((each) => {
                        return {
                          comparisionMethod: each.comparisionMethod,
                          arguments: each.arguments,
                          fieldName: each.fieldName,
                          isFlexField: each.isFlexField,
                        };
                      }),
                    };
                  }),
                },
              }}
              query={useGoldenRecordByTargetingCriteriaQuery}
              queryObjectName='goldenRecordByTargetingCriteria'
            />
          ) : (
            <PaperContainer>
              <Typography variant='h6'>
                Target Population Entries (Households)
              </Typography>
              <Label>Add targeting criteria to see results.</Label>
            </PaperContainer>
          )}
        </Form>
      )}
    </Formik>
  );
}
