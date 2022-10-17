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
import { Field, Form, Formik } from 'formik';
import React, { useState, useEffect, useCallback, ReactElement } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import * as Yup from 'yup';
import { BreadCrumbsItem } from '../../../../components/core/BreadCrumbs';
import { LoadingButton } from '../../../../components/core/LoadingButton';
import { PageHeader } from '../../../../components/core/PageHeader';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { LookUpSelection } from '../../../../components/accountability/Communication/LookUps/LookUpSelection';
import { PaperContainer } from '../../../../components/targeting/PaperContainer';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { usePermissions } from '../../../../hooks/usePermissions';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import {
  CommunicationSteps,
  CommunicationTabsValues,
} from '../../../../utils/constants';
import {
  CreateAccountabilityCommunicationMessageMutationVariables,
  useAllAdminAreasQuery,
  useAllRapidProFlowsQuery,
  useCreateAccountabilityCommunicationMessageMutation,
  useSampleSizeLazyQuery,
} from '../../../../__generated__/graphql';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';
import { TabPanel } from '../../../../components/core/TabPanel';
import { FormikMultiSelectField } from '../../../../shared/Formik/FormikMultiSelectField';
import { FormikRadioGroup } from '../../../../shared/Formik/FormikRadioGroup';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { getPercentage } from '../../../../utils/utils';
import { FormikSliderField } from '../../../../shared/Formik/FormikSliderField';
import { FormikCheckboxField } from '../../../../shared/Formik/FormikCheckboxField';

const steps = ['Recipients Look up', 'Sample Size', 'Details'];
const SampleSizeTabs = ['Full List', 'Random Sampling'];

const Border = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const initialValues = {
  households: [],
  targetPopulation: '',
  registrationDataImport: '',
  confidenceInterval: 95,
  marginOfError: 5,
  filterAgeMin: null,
  filterAgeMax: null,
  filterSex: '',
  excludedAdminAreasFull: [],
  excludedAdminAreasRandom: [],
  verificationChannel: 'MANUAL',
  rapidProFlow: '',
  adminCheckbox: false,
  ageCheckbox: false,
  sexCheckbox: false,
  title: '',
  body: '',
  samplingType: 'FULL_LIST',
};

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareVariables(selectedSampleSizeType, values, businessArea) {
  const variables = {
    input: {
      sampling: selectedSampleSizeType === 0 ? 'FULL_LIST' : 'RANDOM',
      fullListArguments:
        selectedSampleSizeType === 0
          ? {
              excludedAdminAreas: values.excludedAdminAreasFull || [],
            }
          : null,
      verificationChannel: values.verificationChannel,
      rapidProArguments:
        values.verificationChannel === 'RAPIDPRO'
          ? {
              flowId: values.rapidProFlow,
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
      businessAreaSlug: businessArea,
    },
  };
  return variables;
}

export function CreateCommunicationPage(): React.ReactElement {
  const { t } = useTranslation();
  const [
    mutate,
    { loading },
  ] = useCreateAccountabilityCommunicationMessageMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const [activeStep, setActiveStep] = useState(CommunicationSteps.LookUp);
  const [selectedTab, setSelectedTab] = useState(
    CommunicationTabsValues.HOUSEHOLD,
  );
  const [selectedSampleSizeType, setSelectedSampleSizeType] = useState(0);
  const [formValues, setFormValues] = useState(initialValues);
  const [validateData, setValidateData] = useState(false);

  const { data } = useAllAdminAreasQuery({
    variables: {
      first: 100,
      businessArea,
    },
  });

  const { data: rapidProFlows } = useAllRapidProFlowsQuery({
    variables: {
      businessAreaSlug: businessArea,
    },
  });

  const [loadSampleSize, { data: sampleSizesData }] = useSampleSizeLazyQuery({
    variables: prepareVariables(
      selectedSampleSizeType,
      formValues,
      businessArea,
    ),
    fetchPolicy: 'network-only',
  });

  useEffect(() => {
    loadSampleSize();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formValues]);

  const validationSchema = useCallback(() => {
    const datum = {
      title: Yup.string(),
      body: Yup.string(),
    };

    if (activeStep === CommunicationSteps.Details) {
      datum.title = Yup.string()
        .min(2, t('Too short'))
        .max(255, t('Too long'))
        .required(t('Title is required'));
      datum.body = Yup.string()
        .min(2, t('Too short'))
        .required(t('Message is required'));
    }
    setValidateData(true);

    return Yup.object().shape(datum);
  }, [activeStep, t]);

  const validate = (values): { error?: string } => {
    const { households } = values;
    const { targetPopulation } = values;
    const { registrationDataImport } = values;
    const errors: { [key: string]: string | { [key: string]: string } } = {};
    if (
      households.length === 0 &&
      !targetPopulation &&
      !registrationDataImport
    ) {
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
  if (!hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions))
    return <PermissionDenied />;

  const getSampleSizePercentage = (): string => {
    return `(${getPercentage(
      sampleSizesData?.sampleSize?.sampleSize,
      sampleSizesData?.sampleSize?.paymentRecordCount,
    )})`;
  };

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Communication'),
      to: `/${businessArea}/accountability/communication`,
    },
  ];

  const handleNext = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
    setValidateData(false);
  };

  const handleBack = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
  const prepareMutationVariables = (values) => {
    const variables = {
      businessAreaSlug: businessArea,
      inputs: {
        households: values.households,
        targetPopulation: values.targetPopulation,
        registrationDataImport: values.registrationDataImport,
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
        title: values.title,
        body: values.body,
      },
    };
    return variables as CreateAccountabilityCommunicationMessageMutationVariables;
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
            showMessage(t('Communication Ticket created.'), {
              pathname: `/${businessArea}/accountability/communication/${response.data.createAccountabilityCommunicationMessage.message.id}`,
              historyMethod: 'push',
            });
          } catch (e) {
            e.graphQLErrors.map((x) => showMessage(x.message));
          }
        } else {
          handleNext();
        }
      }}
    >
      {({ submitForm, setValues, values, setFieldValue, errors }) => (
        <>
          <PageHeader
            title='New Message'
            breadCrumbs={
              hasPermissions(
                PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE,
                permissions,
              )
                ? breadCrumbsItems
                : null
            }
          />
          <PaperContainer>
            <Grid xs={9} item>
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
              {activeStep === CommunicationSteps.LookUp && (
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
              {activeStep === CommunicationSteps.SampleSize && (
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
                      {SampleSizeTabs.map((tab, index) => (
                        <FormControlLabel
                          value={index}
                          onChange={() => {
                            setFormValues(initialValues);
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
                        Sample size: {sampleSizesData?.sampleSize?.sampleSize}{' '}
                        out of {sampleSizesData?.sampleSize?.paymentRecordCount}{' '}
                        {getSampleSizePercentage()}
                      </Box>
                      <Box fontSize={12} color='#797979'>
                        {t('This option is recommended for RapidPro')}
                      </Box>
                      <Field
                        name='verificationChannel'
                        label={t('Verification Channel')}
                        style={{ flexDirection: 'row' }}
                        choices={[
                          { value: 'RAPIDPRO', name: 'RAPIDPRO' },
                          { value: 'XLSX', name: 'XLSX' },
                          { value: 'MANUAL', name: 'MANUAL' },
                        ]}
                        component={FormikRadioGroup}
                      />
                      {values.verificationChannel === 'RAPIDPRO' && (
                        <Field
                          name='rapidProFlow'
                          label={t('RapidPro Flow')}
                          style={{ width: '90%' }}
                          choices={
                            rapidProFlows
                              ? rapidProFlows.allRapidProFlows.map((flow) => ({
                                  value: flow.id,
                                  name: flow.name,
                                }))
                              : []
                          }
                          component={FormikSelectField}
                        />
                      )}
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
                        Sample size: {sampleSizesData?.sampleSize?.sampleSize}{' '}
                        out of {sampleSizesData?.sampleSize?.paymentRecordCount}
                        {getSampleSizePercentage()}
                      </Box>
                      <Field
                        name='verificationChannel'
                        label={t('Verification Channel')}
                        style={{ flexDirection: 'row' }}
                        choices={[
                          { value: 'RAPIDPRO', name: 'RAPIDPRO' },
                          { value: 'XLSX', name: 'XLSX' },
                          { value: 'MANUAL', name: 'MANUAL' },
                        ]}
                        component={FormikRadioGroup}
                      />
                      {values.verificationChannel === 'RAPIDPRO' && (
                        <Field
                          name='rapidProFlow'
                          label='RapidPro Flow'
                          style={{ width: '90%' }}
                          choices={
                            rapidProFlows
                              ? rapidProFlows.allRapidProFlows.map((flow) => ({
                                  value: flow.id,
                                  name: flow.name,
                                }))
                              : []
                          }
                          component={FormikSelectField}
                        />
                      )}
                    </Box>
                  </TabPanel>
                </Box>
              )}
              {activeStep === CommunicationSteps.Details && (
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
                      />
                    </Grid>
                  </Box>
                  <Grid item xs={12}>
                    <Field
                      name='body'
                      required
                      multiline
                      fullWidth
                      variant='outlined'
                      label={t('Message')}
                      component={FormikTextField}
                    />
                  </Grid>
                </>
              )}
              {dataChangeErrors(errors)}
            </Form>
            <Box pt={3} display='flex' flexDirection='row'>
              <Box mr={3}>
                <Button
                  component={Link}
                  to={`/${businessArea}/acccountability/communication`}
                >
                  {t('Cancel')}
                </Button>
              </Box>
              <Box display='flex' ml='auto'>
                <Button
                  disabled={activeStep === CommunicationSteps.LookUp}
                  onClick={handleBack}
                >
                  {t('Back')}
                </Button>
                <LoadingButton
                  loading={loading}
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                >
                  {activeStep === steps.length - 1 ? t('Save') : t('Next')}
                </LoadingButton>
              </Box>
            </Box>
          </PaperContainer>
        </>
      )}
    </Formik>
  );
}
