import React from 'react';
import styled from 'styled-components';
import { useParams } from 'react-router-dom';
import { Button } from '@material-ui/core';
import { Field, Form, Formik } from 'formik';
import { PageHeader } from '../PageHeader';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { BreadCrumbsItem } from '../BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import {
  useAllProgramsQuery,
  useUpdateTpMutation,
} from '../../__generated__/graphql';
import { useSnackbar } from '../../hooks/useSnackBar';
import { TARGET_POPULATION_QUERY } from '../../apollo/queries/TargetPopulation';
import { getTargetingCriteriaVariables } from '../../utils/targetingUtils';
import { CandidateListTab } from './Edit/CandidateListTab';
import { TargetPopulationProgramme } from './TargetPopulationProgramme';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

interface EditTargetPopulationProps {
  targetPopulationCriterias?;
  cancelEdit?;
  targetPopulation?;
}

export function EditTargetPopulation({
  targetPopulationCriterias,
  cancelEdit,
  targetPopulation,
}: EditTargetPopulationProps): React.ReactElement {
  const initialValues = {
    id: targetPopulation.id,
    name: targetPopulation.name || '',
    program: targetPopulation.program?.id || '',
    criterias: targetPopulationCriterias.rules || [],
    candidateListCriterias:
      targetPopulation.candidateListTargetingCriteria?.rules || [],
    targetPopulationCriterias:
      targetPopulation.finalListTargetingCriteria?.rules || [],
  };
  const [mutate] = useUpdateTpMutation();
  const { showMessage } = useSnackbar();
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Targeting',
      to: `/${businessArea}/target-population/`,
    },
  ];
  const {
    data: allProgramsData,
    loading: loadingPrograms,
  } = useAllProgramsQuery({
    variables: { businessArea, status: ['ACTIVE'] },
  });
  const isTitleEditable = (): boolean => {
    switch (targetPopulation.status) {
      case 'APPROVED':
        return false;
      default:
        return true;
    }
  };

  const handleValidate = (values): { candidateListCriterias?: string } => {
    const { candidateListCriterias } = values;
    const errors: { candidateListCriterias?: string } = {};
    if (!candidateListCriterias.length) {
      errors.candidateListCriterias =
        'You need to select at least one targeting criteria';
    }
    return errors;
  };

  return (
    <Formik
      initialValues={initialValues}
      validate={handleValidate}
      onSubmit={async (values) => {
        await mutate({
          variables: {
            input: {
              id: values.id,
              programId: values.program,
              ...(targetPopulation.status === 'DRAFT' && { name: values.name }),
              ...getTargetingCriteriaVariables({
                criterias: values.candidateListCriterias,
              }),
            },
          },
          refetchQueries: [
            {
              query: TARGET_POPULATION_QUERY,
              variables: {
                id,
              },
            },
          ],
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
                  label='Enter Target Population Name'
                  type='text'
                  fullWidth
                  required
                  component={FormikTextField}
                />
              ) : (
                values.name
              )
            }
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
                  disabled={
                    values.criterias?.length +
                      values.candidateListCriterias?.length ===
                      0 || !values.name
                  }
                >
                  Save
                </Button>
              </ButtonContainer>
            </>
          </PageHeader>
          <TargetPopulationProgramme
            allPrograms={allProgramsData}
            loading={loadingPrograms}
            program={values.program}
          />
          <CandidateListTab values={values} />
        </Form>
      )}
    </Formik>
  );
}
