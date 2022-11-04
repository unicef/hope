import {
  Box,
  Button,
  FormControlLabel,
  FormHelperText,
  Grid,
  Radio,
  RadioGroup,
  Step,
  StepLabel,
  Stepper,
  Typography,
} from '@material-ui/core';
import { Link, useHistory } from 'react-router-dom';
import { Field, Form, Formik } from 'formik';
import React, { ReactElement, useCallback, useEffect, useState } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { BreadCrumbsItem } from '../../../../components/core/BreadCrumbs';
import { LoadingButton } from '../../../../components/core/LoadingButton';
import { PageHeader } from '../../../../components/core/PageHeader';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { LookUpSelection } from '../../../../components/accountability/Surveys/LookUps/LookUpSelection';
import { PaperContainer } from '../../../../components/targeting/PaperContainer';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { usePermissions } from '../../../../hooks/usePermissions';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { SurveySteps, SurveyTabsValues } from '../../../../utils/constants';
import {
  AccountabilitySampleSizeQueryVariables,
  CreateSurveyAccountabilityMutationVariables,
  useAccountabilitySampleSizeLazyQuery,
  useAllAdminAreasQuery,
  useCreateSurveyAccountabilityMutation,
} from '../../../../__generated__/graphql';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';
import { TabPanel } from '../../../../components/core/TabPanel';
import { FormikMultiSelectField } from '../../../../shared/Formik/FormikMultiSelectField';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { getPercentage } from '../../../../utils/utils';
import { FormikSliderField } from '../../../../shared/Formik/FormikSliderField';
import { FormikCheckboxField } from '../../../../shared/Formik/FormikCheckboxField';
import { useConfirmation } from '../../../../components/core/ConfirmationDialog';
import { FormikEffect } from '../../../../components/core/FormikEffect';

const steps = ['Recipients Look up', 'Sample Size', 'Details'];
const sampleSizeTabs = ['Full List', 'Random Sampling'];

const Border = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

function prepareVariables(
  selectedSampleSizeType,
  values,
): AccountabilitySampleSizeQueryVariables {
  return {
    input: {
      targetPopulation: values.targetPopulation,
      program: values.program,
      samplingType: selectedSampleSizeType === 0 ? 'FULL_LIST' : 'RANDOM',
      fullListArguments:
        selectedSampleSizeType === 0
          ? {
              excludedAdminAreas: values.excludedAdminAreasFull || [],
            }
          : null,
      randomSamplingArguments:
        selectedSampleSizeType === 1
          ? {
              confidenceInterval: values.confidenceInterval * 0.01,
              marginOfError: values.marginOfError * 0.01,
              excludedAdminAreas: values.adminCheckbox
                ? values.excludedAdminAreasRandom
                : [],
              age: values.ageCheckbox
                ? { min: values.filterAgeMin, max: values.filterAgeMax }
                : null,
              sex: values.sexCheckbox ? values.filterSex : null,
            }
          : null,
    },
  };
}

export const CreateSurveyPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const [mutate, { loading }] = useCreateSurveyAccountabilityMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const confirm = useConfirmation();

  const category = history.location.state?.category;

  const initialValues = {
    category,
    message: '',
    program: '',
    targetPopulation: '',
    confidenceInterval: 95,
    marginOfError: 5,
    filterAgeMin: null,
    filterAgeMax: null,
    filterSex: '',
    excludedAdminAreasFull: [],
    excludedAdminAreasRandom: [],
    adminCheckbox: false,
    ageCheckbox: false,
    sexCheckbox: false,
    title: '',
    samplingType: 'FULL_LIST',
  };

  const [activeStep, setActiveStep] = useState(SurveySteps.LookUp);
  const [selectedTab, setSelectedTab] = useState(SurveyTabsValues.PROGRAM);
  const [selectedSampleSizeType, setSelectedSampleSizeType] = useState(0);
  const [formValues, setFormValues] = useState(initialValues);
  const [validateData, setValidateData] = useState(false);

  const { data } = useAllAdminAreasQuery({
    variables: {
      first: 100,
      businessArea,
    },
  });

  const [
    loadSampleSize,
    { data: sampleSizesData },
  ] = useAccountabilitySampleSizeLazyQuery({
    variables: prepareVariables(selectedSampleSizeType, formValues),
    fetchPolicy: 'network-only',
  });

  useEffect(() => {
    if (activeStep === SurveySteps.SampleSize) {
      loadSampleSize();
    }
  }, [activeStep, formValues, loadSampleSize]);

  const validationSchema = useCallback(() => {
    const datum = {
      title: Yup.string(),
      message: Yup.string(),
    };
    if (activeStep === SurveySteps.Details) {
      datum.title = Yup.string()
        .min(2, t('Too short'))
        .max(255, t('Too long'))
        .required(t('Title is required'));
      if (category === 'SMS') {
        datum.message = Yup.string()
          .min(2, t('Too short'))
          .max(255, t('Too long'))
          .required(t('Message is required'));
      }
    }
    setValidateData(true);

    return Yup.object().shape(datum);
  }, [activeStep, t, category]);

  const validate = (values): { error?: string } => {
    const { program, targetPopulation } = values;
    const errors: { [key: string]: string | { [key: string]: string } } = {};
    if (!targetPopulation && !program) {
      errors.error = t('Field Selection is required');
    }
    return errors;
  };

  const mappedAdminAreas = data?.allAdminAreas?.edges?.length
    ? data.allAdminAreas.edges.map((el) => ({
        value: el.node.id,
        name: el.node.name,
      }))
    : [];

  if (permissions === null) return null;
  if (
    !hasPermissions(PERMISSIONS.ACCOUNTABILITY_SURVEY_VIEW_CREATE, permissions)
  )
    return <PermissionDenied />;

  const getSampleSizePercentage = (): string => {
    return `(${getPercentage(
      sampleSizesData?.accountabilitySampleSize?.sampleSize,
      sampleSizesData?.accountabilitySampleSize?.numberOfRecipients,
    )})`;
  };

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Surveys'),
      to: `/${businessArea}/accountability/surveys`,
    },
  ];

  const handleNext = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
    setValidateData(false);
  };

  const handleBack = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const prepareMutationVariables = (
    values,
  ): CreateSurveyAccountabilityMutationVariables => {
    return {
      input: {
        title: values.title,
        body: values.body,
        category: values.category,
        targetPopulation: values.targetPopulation,
        program: values.program,
        samplingType: selectedSampleSizeType === 0 ? 'FULL_LIST' : 'RANDOM',
        fullListArguments:
          selectedSampleSizeType === 0
            ? {
                excludedAdminAreas: values.excludedAdminAreasFull,
              }
            : null,
        randomSamplingArguments:
          selectedSampleSizeType === 1
            ? {
                excludedAdminAreas: values.excludedAdminAreasRandom,
                confidenceInterval: values.confidenceInterval * 0.01,
                marginOfError: values.marginOfError * 0.01,
                age: values.ageCheckbox
                  ? { min: values.filterAgeMin, max: values.filterAgeMax }
                  : null,
                sex: values.sexCheckbox ? values.filterSex : null,
              }
            : null,
      },
    };
  };

  const dataChangeErrors = (errors): ReactElement[] =>
    ['error'].map((fieldname) => (
      <FormHelperText key={fieldname} error>
        {errors[fieldname]}
      </FormHelperText>
    ));

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      validate={(values) => validate(values)}
      validateOnBlur={validateData}
      validateOnChange={validateData}
      onSubmit={async (values) => {
        if (activeStep === steps.length - 1) {
          try {
            const response = await mutate({
              variables: prepareMutationVariables(values),
            });
            showMessage(t('Survey created.'), {
              pathname: `/${businessArea}/accountability/surveys/${response.data.createSurvey.survey.id}`,
              historyMethod: 'push',
            });
          } catch (e) {
            e.graphQLErrors.map((x) => showMessage(x.message));
          }
        } else {
          setFormValues(values);
          handleNext();
        }
      }}
    >
      {({ submitForm, setValues, values, setFieldValue, errors }) => (
        <>
          <PageHeader
            title='New Survey'
            breadCrumbs={
              hasPermissions(
                PERMISSIONS.ACCOUNTABILITY_SURVEY_VIEW_CREATE,
                permissions,
              )
                ? breadCrumbsItems
                : null
            }
          />
          <PaperContainer>
            <Grid xs={12} item>
              <Stepper activeStep={activeStep}>
                {steps.map((label) => {
                  const stepProps: { completed?: boolean } = {};
                  const labelProps: {
                    optional?: React.ReactNode;
                  } = {};
                  return (
                    <Step key={label} {...stepProps}>
                      <StepLabel {...labelProps}>{label}</StepLabel>
                    </Step>
                  );
                })}
              </Stepper>
            </Grid>
            <Form>
              <FormikEffect
                values={values}
                onChange={() => setFormValues(values)}
              />
              {activeStep === SurveySteps.LookUp && (
                <Box display='flex' flexDirection='column'>
                  <LookUpSelection
                    businessArea={businessArea}
                    values={values}
                    onValueChange={setFieldValue}
                    setValues={setValues}
                    selectedTab={selectedTab}
                    setSelectedTab={setSelectedTab}
                  />
                </Box>
              )}
              {activeStep === SurveySteps.SampleSize && (
                <Box px={8}>
                  <Box display='flex' alignItems='center'>
                    <Box pr={5} fontWeight='500' fontSize='medium'>
                      {t('Sample Size')}:
                    </Box>
                    <RadioGroup
                      aria-labelledby='selection-radio-buttons-group'
                      value={selectedSampleSizeType}
                      row
                      name='radio-buttons-group'
                    >
                      {sampleSizeTabs.map((tab, index) => (
                        <FormControlLabel
                          value={index}
                          onChange={() => {
                            setFormValues(values);
                            setSelectedSampleSizeType(index);
                          }}
                          key={tab}
                          control={<Radio color='primary' />}
                          label={tab}
                        />
                      ))}
                    </RadioGroup>
                  </Box>
                  <TabPanel value={selectedSampleSizeType} index={0}>
                    {mappedAdminAreas && (
                      <Field
                        name='excludedAdminAreasFull'
                        choices={mappedAdminAreas}
                        variant='outlined'
                        label={t('Filter Out Administrative Level Areas')}
                        component={FormikMultiSelectField}
                      />
                    )}
                    <Box pt={3}>
                      <Box
                        pb={3}
                        pt={3}
                        fontSize={16}
                        fontWeight='fontWeightBold'
                      >
                        Sample size:{' '}
                        {sampleSizesData?.accountabilitySampleSize?.sampleSize}{' '}
                        out of{' '}
                        {
                          sampleSizesData?.accountabilitySampleSize
                            ?.numberOfRecipients
                        }{' '}
                        {getSampleSizePercentage()}
                      </Box>
                      <Box fontSize={12} color='#797979'>
                        {t('This option is recommended for RapidPro')}
                      </Box>
                    </Box>
                  </TabPanel>
                  <TabPanel value={selectedSampleSizeType} index={1}>
                    <Box pt={3}>
                      <Field
                        name='confidenceInterval'
                        label={t('Confidence Interval')}
                        min={90}
                        max={99}
                        component={FormikSliderField}
                        suffix='%'
                      />
                      <Field
                        name='marginOfError'
                        label={t('Margin of Error')}
                        min={0}
                        max={9}
                        component={FormikSliderField}
                        suffix='%'
                      />
                      <Typography variant='caption'>
                        {t('Cluster Filters')}
                      </Typography>
                      <Box flexDirection='column' display='flex'>
                        <Box display='flex'>
                          <Field
                            name='adminCheckbox'
                            label={t('Administrative Level')}
                            component={FormikCheckboxField}
                          />
                          <Field
                            name='ageCheckbox'
                            label={t('Age of HoH')}
                            component={FormikCheckboxField}
                          />
                          <Field
                            name='sexCheckbox'
                            label={t('Gender of HoH')}
                            component={FormikCheckboxField}
                          />
                        </Box>
                        {values.adminCheckbox && (
                          <Field
                            name='excludedAdminAreasRandom'
                            choices={mappedAdminAreas}
                            variant='outlined'
                            label={t('Filter Out Administrative Level Areas')}
                            component={FormikMultiSelectField}
                          />
                        )}

                        <Grid container>
                          {values.ageCheckbox && (
                            <Grid item xs={12}>
                              <Grid container>
                                <Grid item xs={4}>
                                  <Field
                                    name='filterAgeMin'
                                    label={t('Minimum Age')}
                                    type='number'
                                    color='primary'
                                    component={FormikTextField}
                                  />
                                </Grid>
                                <Grid item xs={4}>
                                  <Field
                                    name='filterAgeMax'
                                    label={t('Maximum Age')}
                                    type='number'
                                    color='primary'
                                    component={FormikTextField}
                                  />
                                </Grid>
                              </Grid>
                            </Grid>
                          )}
                          {values.sexCheckbox && (
                            <Grid item xs={5}>
                              <Field
                                name='filterSex'
                                label={t('Gender')}
                                color='primary'
                                choices={[
                                  { value: 'FEMALE', name: t('Female') },
                                  { value: 'MALE', name: t('Male') },
                                ]}
                                component={FormikSelectField}
                              />
                            </Grid>
                          )}
                        </Grid>
                      </Box>
                      <Box
                        pb={3}
                        pt={3}
                        fontSize={16}
                        fontWeight='fontWeightBold'
                      >
                        Sample size:{' '}
                        {sampleSizesData?.accountabilitySampleSize?.sampleSize}{' '}
                        out of{' '}
                        {
                          sampleSizesData?.accountabilitySampleSize
                            ?.numberOfRecipients
                        }{' '}
                        {getSampleSizePercentage()}
                      </Box>
                    </Box>
                  </TabPanel>
                </Box>
              )}
              {activeStep === SurveySteps.Details && (
                <>
                  <Border />
                  <Box my={3}>
                    <Grid item xs={12}>
                      <Field
                        name='title'
                        required
                        multiline
                        fullWidth
                        variant='outlined'
                        label={t('Title')}
                        component={FormikTextField}
                        data-cy='input-title'
                      />
                    </Grid>
                  </Box>
                  {category === 'SMS' && (
                    <Box my={3}>
                      <Grid item xs={12}>
                        <Field
                          name='body'
                          required
                          multiline
                          fullWidth
                          variant='outlined'
                          label={t('Message')}
                          component={FormikTextField}
                          data-cy='input-body'
                        />
                      </Grid>
                    </Box>
                  )}
                  <Grid item xs={12}>
                    <Box
                      pb={3}
                      pt={3}
                      fontSize={16}
                      fontWeight='fontWeightBold'
                    >
                      {t('Number of selected recipients')}:{' '}
                      {
                        sampleSizesData?.accountabilitySampleSize
                          ?.numberOfRecipients
                      }
                    </Box>
                  </Grid>
                </>
              )}
              {dataChangeErrors(errors)}
            </Form>
            <Box pt={3} display='flex' flexDirection='row'>
              <Box mr={3}>
                <Button
                  component={Link}
                  to={`/${businessArea}/accountability/surveys`}
                >
                  {t('Cancel')}
                </Button>
              </Box>
              <Box display='flex' ml='auto'>
                <Button
                  disabled={activeStep === SurveySteps.LookUp}
                  onClick={handleBack}
                >
                  {t('Back')}
                </Button>

                {activeStep === steps.length - 1 ? (
                  <Button
                    onClick={() =>
                      confirm({
                        content: t(
                          'Are you sure you want to send this survey?',
                        ),
                        continueText: 'Save',
                      }).then(() => submitForm())
                    }
                    variant='contained'
                    color='primary'
                  >
                    {t('Save')}
                  </Button>
                ) : (
                  <LoadingButton
                    loading={loading}
                    color='primary'
                    variant='contained'
                    onClick={submitForm}
                    data-cy='button-submit'
                  >
                    {t('Next')}
                  </LoadingButton>
                )}
              </Box>
            </Box>
          </PaperContainer>
        </>
      )}
    </Formik>
  );
};
