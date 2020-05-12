import React from 'react';
import styled from 'styled-components';
import { Button, Typography, Paper, Tabs, Tab } from '@material-ui/core';
import { Field, Form, Formik, FieldArray } from 'formik';
import { PageHeader } from '../../components/PageHeader';
import { TargetingCriteria } from '../../components/TargetPopulation/TargetingCriteria';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { Results } from '../../components/TargetPopulation/Results';
import { useCreateTpMutation } from '../../__generated__/graphql';
import { useSnackbar } from '../../hooks/useSnackBar';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { CreateTable } from '../tables/TargetPopulation/Create';

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
      <Tab label='Programme Population' />
      <Tab label='Target Population' disabled />
    </Tabs>
  );
  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        mutate({
          variables: {
            input: {
              name: values.name,
              businessAreaSlug: businessArea,
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
        }).then(
          (res) => {
            return showMessage('Target Population Created', {
              pathname: `/${businessArea}/target-population/${res.data.createTargetPopulation.targetPopulation.id}`,
              historyMethod: 'push',
            });
          },
          () => {
            return showMessage('Name already exist');
          },
        );
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
                candidateListRules={values.criterias}
                isEdit
              />
            )}
          />
          <Results />
          {values.criterias.length ? (
            <CreateTable
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
