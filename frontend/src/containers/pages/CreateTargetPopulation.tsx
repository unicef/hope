import React from 'react';
import * as Yup from 'yup';
import styled from 'styled-components';
import { Button, Paper, Typography } from '@material-ui/core';
import { Field, FieldArray, Form, Formik } from 'formik';
import { PageHeader } from '../../components/PageHeader';
import { TargetingCriteria } from '../../components/TargetPopulation/TargetingCriteria';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { Results } from '../../components/TargetPopulation/Results';
import {
  useCreateTpMutation,
  useAllProgramsQuery,
} from '../../__generated__/graphql';
import { useSnackbar } from '../../hooks/useSnackBar';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { CreateTable } from '../tables/TargetPopulation/Create';
import { getTargetingCriteriaVariables } from '../../utils/targetingUtils';
import { TargetPopulationProgramme } from '../../components/TargetPopulation/TargetPopulationProgramme';
import { TargetingCriteriaDisabled } from '../../components/TargetPopulation/TargetingCriteria/TargetingCriteriaDisabled';
import { usePermissions } from '../../hooks/usePermissions';
import { LoadingComponent } from '../../components/LoadingComponent';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { PermissionDenied } from '../../components/PermissionDenied';
import {
  getFullNodeFromEdgesById,
  handleValidationErrors,
} from '../../utils/utils';

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

export function CreateTargetPopulation(): React.ReactElement {
  const initialValues = {
    name: '',
    criterias: [],
    program: null,
  };
  const [mutate] = useCreateTpMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const {
    data: allProgramsData,
    loading: loadingPrograms,
  } = useAllProgramsQuery({
    variables: { businessArea, status: ['ACTIVE'] },
  });

  if (loadingPrograms) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions))
    return <PermissionDenied />;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Targeting',
      to: `/${businessArea}/target-population/`,
    },
  ];
  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .min(2, 'Too short')
      .max(255, 'Too long'),
  });

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={async (values, { setFieldError }) => {
        try {
          const res = await mutate({
            variables: {
              input: {
                programId: values.program,
                name: values.name,
                businessAreaSlug: businessArea,
                ...getTargetingCriteriaVariables(values),
              },
            },
          });
          showMessage('Target Population Created', {
            pathname: `/${businessArea}/target-population/${res.data.createTargetPopulation.targetPopulation.id}`,
            historyMethod: 'push',
          });
        } catch (e) {
          const { nonValidationErrors } = handleValidationErrors(
            'createTargetPopulation',
            e,
            setFieldError,
            showMessage,
          );
          if (nonValidationErrors.length > 0) {
            showMessage('Unexpected problem while creating Target Population');
          }
        }
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
            breadCrumbs={
              hasPermissions(PERMISSIONS.TARGETING_VIEW_LIST, permissions)
                ? breadCrumbsItems
                : null
            }
            hasInputComponent
          >
            <>
              <ButtonContainer>
                <Button
                  variant='contained'
                  color='primary'
                  onClick={submitForm}
                  disabled={values.criterias?.length === 0 || !values.name}
                  data-cy='button-target-population-create'
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
          {values.program ? (
            <FieldArray
              name='criterias'
              render={(arrayHelpers) => (
                <TargetingCriteria
                  helpers={arrayHelpers}
                  candidateListRules={values.criterias}
                  isEdit
                  selectedProgram={getFullNodeFromEdgesById(
                    allProgramsData?.allPrograms?.edges,
                    values.program,
                  )}
                />
              )}
            />
          ) : (
            <TargetingCriteriaDisabled />
          )}
          <Results />
          {values.criterias.length ? (
            <CreateTable
              variables={getTargetingCriteriaVariables(values)}
              program={values.program}
              businessArea={businessArea}
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
