import { Button } from '@material-ui/core';
import { Field, Form, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import { TARGET_POPULATION_QUERY } from '../../apollo/queries/TargetPopulation';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useSnackbar } from '../../hooks/useSnackBar';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { getTargetingCriteriaVariables } from '../../utils/targetingUtils';
import {
  getFullNodeFromEdgesById,
  handleValidationErrors,
} from '../../utils/utils';
import {
  useAllProgramsQuery,
  useUpdateTpMutation,
} from '../../__generated__/graphql';
import { BreadCrumbsItem } from '../BreadCrumbs';
import { PageHeader } from '../PageHeader';
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
  const { t } = useTranslation();
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
      title: t('Targeting'),
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
      errors.candidateListCriterias = t(
        'You need to select at least one targeting criteria',
      );
    }
    return errors;
  };
  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .min(2, 'Too short')
      .max(255, 'Too long'),
  });

  return (
    <Formik
      initialValues={initialValues}
      validate={handleValidate}
      validationSchema={validationSchema}
      onSubmit={async (values, { setFieldError }) => {
        try {
          await mutate({
            variables: {
              input: {
                id: values.id,
                programId: values.program,
                ...(targetPopulation.status === 'DRAFT' && {
                  name: values.name,
                }),
                ...getTargetingCriteriaVariables({
                  criterias: values.candidateListCriterias,
                }),
              },
            },
            refetchQueries: () => [
              {
                query: TARGET_POPULATION_QUERY,
                variables: {
                  id,
                },
              },
            ],
          });
          cancelEdit();
          showMessage(t('Target Population Updated'), {
            pathname: `/${businessArea}/target-population/${values.id}`,
            historyMethod: 'push',
          });
        } catch (e) {
          const { nonValidationErrors } = handleValidationErrors(
            'updateTargetPopulation',
            e,
            setFieldError,
            showMessage,
          );
          if (nonValidationErrors.length > 0) {
            showMessage(
              t('Unexpected problem while creating Target Population'),
            );
          }
        }
      }}
    >
      {({ values }) => (
        <Form>
          <PageHeader
            title={
              isTitleEditable() ? (
                <Field
                  name='name'
                  label={t('Enter Target Population Name')}
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
                    {t('Cancel')}
                  </Button>
                </ButtonContainer>
              )}
              <ButtonContainer>
                <Button
                  variant='contained'
                  color='primary'
                  type='submit'
                  disabled={
                    values.criterias?.length +
                      values.candidateListCriterias?.length ===
                      0 || !values.name
                  }
                >
                  {t('Save')}
                </Button>
              </ButtonContainer>
            </>
          </PageHeader>
          <TargetPopulationProgramme
            allPrograms={allProgramsData}
            loading={loadingPrograms}
            program={values.program}
          />
          <CandidateListTab
            values={values}
            selectedProgram={getFullNodeFromEdgesById(
              allProgramsData?.allPrograms?.edges,
              values.program,
            )}
            businessArea={businessArea}
          />
        </Form>
      )}
    </Formik>
  );
}
