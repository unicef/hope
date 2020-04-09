import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Button, Typography, Paper, Tabs, Tab } from '@material-ui/core';
import { Field, Form, Formik, FieldArray } from 'formik';
import { PageHeader } from '../../components/PageHeader';
import { TargetingCriteria } from '../../components/TargetPopulation/TargetingCriteria';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { Results } from '../../components/TargetPopulation/Results';
import { TargetPopulationHouseholdTable } from '../tables/TargetPopulationHouseholdTable';
import {
  useGoldenRecordByTargetingCriteriaQuery,
  useCreateTpMutation,
} from '../../__generated__/graphql';
import { useSnackbar } from '../../hooks/useSnackBar';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';

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

export function CreateTargetPopulation() {
  const { t } = useTranslation();
  const initialValues = {
    name: '',
    criterias: [],
  };
  const [mutate] = useCreateTpMutation();
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
        showMessage('Target Population Created', {
          pathname: `/${businessArea}/target-population/${data.createTargetPopulation.targetPopulation.id}`,
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
                label='Enter Target Population Name'
                type='text'
                fullWidth
                required
                component={FormikTextField}
              />
            }
            breadCrumbs={breadCrumbsItems}
            tabs={tabs}
            hasInputComponent
          >
            <>
              <ButtonContainer>
                <Button
                  variant='contained'
                  color='primary'
                  onClick={submitForm}
                  disabled={!values.name || !values.criterias.length}
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
