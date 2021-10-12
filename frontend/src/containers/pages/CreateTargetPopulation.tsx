import {
  Box,
  Button,
  Collapse,
  Grid,
  Paper,
  Typography,
} from '@material-ui/core';
import KeyboardArrowDown from '@material-ui/icons/KeyboardArrowDown';
import KeyboardArrowUp from '@material-ui/icons/KeyboardArrowUp';
import { Field, FieldArray, Form, Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import * as Yup from 'yup';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { LoadingComponent } from '../../components/LoadingComponent';
import { PageHeader } from '../../components/PageHeader';
import { PermissionDenied } from '../../components/PermissionDenied';
import { Results } from '../../components/TargetPopulation/Results';
import { TargetingCriteria } from '../../components/TargetPopulation/TargetingCriteria';
import { TargetingCriteriaDisabled } from '../../components/TargetPopulation/TargetingCriteria/TargetingCriteriaDisabled';
import { TargetPopulationProgramme } from '../../components/TargetPopulation/TargetPopulationProgramme';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { usePermissions } from '../../hooks/usePermissions';
import { useSnackbar } from '../../hooks/useSnackBar';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { getTargetingCriteriaVariables } from '../../utils/targetingUtils';
import {
  getFullNodeFromEdgesById,
  handleValidationErrors,
} from '../../utils/utils';
import {
  useAllProgramsQuery,
  useCreateTpMutation,
} from '../../__generated__/graphql';
import { CreateTable } from '../tables/TargetPopulation/Create';

export const PaperContainer = styled(Paper)`
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
  const [isExclusionsOpen, setExclusionsOpen] = useState(false);
  const { t } = useTranslation();
  const initialValues = {
    name: '',
    criterias: [],
    program: null,
    excludedIds: '',
    exclusionReason: '',
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
      title: t('Targeting'),
      to: `/${businessArea}/target-population/`,
    },
  ];
  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .min(2, t('Too short'))
      .max(255, t('Too long')),
    excludedIds: Yup.string()
      .max(500, t('Too long'))
      .test('testName', 'ID is not in the correct format', (ids) => {
        const idsArr = ids.split(', ');
        return idsArr.every((el) => /^(IND|HH)-\d{2}-\d{4}\.\d{4}$/.test(el));
      }),
    exclusionReason: Yup.string().max(500, t('Too long')),
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
                excludedIds: values.excludedIds,
                exclusionReason: values.exclusionReason,
                businessAreaSlug: businessArea,
                ...getTargetingCriteriaVariables(values),
              },
            },
          });
          showMessage(t('Target Population Created'), {
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
            showMessage(
              t('Unexpected problem while creating Target Population'),
            );
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
                label={t('Enter Target Population Name')}
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
          <PaperContainer>
            <Box display='flex' justifyContent='space-between'>
              <Typography variant='h6'>
                {t(
                  'Excluded Target Population Entries (Households or Individuals)',
                )}
              </Typography>
              <Button
                variant='outlined'
                color='primary'
                onClick={() => setExclusionsOpen(!isExclusionsOpen)}
                endIcon={
                  isExclusionsOpen ? <KeyboardArrowUp /> : <KeyboardArrowDown />
                }
              >
                {isExclusionsOpen ? t('HIDE') : t('SHOW')}
              </Button>
            </Box>
            <Collapse in={isExclusionsOpen}>
              <Box mt={2}>
                <Grid item xs={6}>
                  <Field
                    name='excludedIds'
                    fullWidth
                    variant='outlined'
                    label={t('Household or Individual IDs to exclude')}
                    component={FormikTextField}
                  />
                </Grid>
              </Box>
              <Box mt={2}>
                <Grid container>
                  <Grid item xs={6}>
                    <Field
                      name='exclusionReason'
                      fullWidth
                      multiline
                      variant='outlined'
                      label={t('Exclusion Reason')}
                      component={FormikTextField}
                    />
                  </Grid>
                </Grid>
              </Box>
            </Collapse>
          </PaperContainer>
          <Results />
          {values.criterias.length ? (
            <CreateTable
              variables={{
                ...getTargetingCriteriaVariables(values),
                excludedIds: values.excludedIds,
              }}
              program={values.program}
              businessArea={businessArea}
            />
          ) : (
            <PaperContainer>
              <Typography variant='h6'>
                {t('Target Population Entries (Households)')}
              </Typography>
              <Label>{t('Add targeting criteria to see results.')}</Label>
            </PaperContainer>
          )}
        </Form>
      )}
    </Formik>
  );
}
