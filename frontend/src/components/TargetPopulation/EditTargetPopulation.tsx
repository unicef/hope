import React from 'react';
import styled from 'styled-components';
import { Button, Tabs, Tab } from '@material-ui/core';
import { Formik, Form, Field } from 'formik';
import { PageHeader } from '../PageHeader';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { BreadCrumbsItem } from '../BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useUpdateTpMutation } from '../../__generated__/graphql';
import { useSnackbar } from '../../hooks/useSnackBar';
import { TabPanel } from '../TabPanel';
import { CandidateListTab } from './Edit/CandidateListTab';
import { TargetPopulationTab } from './Edit/TargetPopulationTab';
import { TargetPopulationDetails } from './TargetPopulationDetails';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

interface EditTargetPopulationProps {
  targetPopulationCriterias?;
  cancelEdit?;
  selectedTab?: number;
  targetPopulation?;
}

export function EditTargetPopulation({
  targetPopulationCriterias,
  cancelEdit,
  selectedTab = 0,
  targetPopulation,
}: EditTargetPopulationProps) {
  const initialValues = {
    id: targetPopulation.id,
    name: targetPopulation.name || '',
    criterias: targetPopulationCriterias.rules || [],
    candidateListCriterias: targetPopulation.candidateListTargetingCriteria?.rules || [],
    targetPopulationCriterias: targetPopulation.finalListTargetingCriteria?.rules || [],
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
      value={selectedTab}
      aria-label='tabs'
      indicatorColor='primary'
      textColor='primary'
    >
      <Tab label='Programme Population' disabled={selectedTab !== 0} />
      <Tab label='Target Population' disabled={selectedTab !== 1} />
    </Tabs>
  );
  const isTitleEditable = () => {
    switch (targetPopulation.status) {
      case 'APPROVED':
        return false;
      default:
        return true;
    }
  };
  const mapRules = (status, values) => {
    switch(status) {
      case 'DRAFT':
        return values.candidateListCriterias.map((rule) => {
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
        })
      default:
        return values.targetPopulationCriterias.map((rule) => {
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
        })
    }
  }
  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        console.log(values)
        const { data } = await mutate({
          variables: {
            input: {
              id: values.id,
              ...(targetPopulation.status === 'DRAFT' && { name: values.name }),
              targetingCriteria: {
                rules: mapRules(targetPopulation.status, values)
              },
            },
          },
        });
        cancelEdit();
        showMessage('Target Population Updated', {
          pathname: `/${businessArea}/target-population/${values.id}`,
          historyMethod: 'push',
        });
      }}
    >
      {({ submitForm, values }) => (
        <Form>
          <PageHeader
            title={
              isTitleEditable() ? (
                <Field
                  name='name'
                  label='Programme Name'
                  type='text'
                  fullWidth
                  required
                  component={FormikTextField}
                />
              ) : (
                values.name
              )
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
          <TabPanel value={selectedTab} index={0}>
            <CandidateListTab values={values} />
          </TabPanel>
          <TabPanel value={selectedTab} index={1}>
            <TargetPopulationDetails targetPopulation={targetPopulation} />
            <TargetPopulationTab values={values} selectedTab={selectedTab} />
          </TabPanel>
        </Form>
      )}
    </Formik>
  );
}
