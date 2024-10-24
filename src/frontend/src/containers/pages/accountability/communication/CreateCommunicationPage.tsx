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
} from '@mui/material';
import { Field, Form, Formik } from 'formik';
import { ReactElement, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import {
  AccountabilityCommunicationMessageSampleSizeQueryVariables,
  CreateAccountabilityCommunicationMessageMutationVariables,
  SamplingChoices,
  useAccountabilityCommunicationMessageSampleSizeLazyQuery,
  useAllAdminAreasQuery,
  useCreateAccountabilityCommunicationMessageMutation,
  useSurveyAvailableFlowsLazyQuery,
} from '@generated/graphql';
import { LookUpSelectionCommunication } from '@components/accountability/Communication/LookUpsCommunication/LookUpSelectionCommunication';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { useConfirmation } from '@components/core/ConfirmationDialog';
import { FormikEffect } from '@components/core/FormikEffect';
import { LoadingButton } from '@components/core/LoadingButton';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TabPanel } from '@components/core/TabPanel';
import { PaperContainer } from '@components/targeting/PaperContainer';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { FormikMultiSelectField } from '@shared/Formik/FormikMultiSelectField';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikSliderField } from '@shared/Formik/FormikSliderField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { CommunicationSteps, CommunicationTabsValues } from '@utils/constants';
import { getPercentage } from '@utils/utils';
import * as React from 'react';

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
  adminCheckbox: false,
  ageCheckbox: false,
  sexCheckbox: false,
  title: '',
  body: '',
  samplingType: SamplingChoices.FullList,
};

function prepareVariables(
  selectedSampleSizeType,
  values,
): AccountabilityCommunicationMessageSampleSizeQueryVariables {
  return {
    input: {
      households: values.households,
      targetPopulation: values.targetPopulation,
      registrationDataImport: values.registrationDataImport,
      samplingType:
        selectedSampleSizeType === 0
          ? SamplingChoices.FullList
          : SamplingChoices.Random,
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

export const CreateCommunicationPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const [mutate, { loading }] =
    useCreateAccountabilityCommunicationMessageMutation();
  const { showMessage } = useSnackbar();
  const navigate = useNavigate();
  const { baseUrl, businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const confirm = useConfirmation();

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

  const [loadSampleSize, { data: sampleSizesData }] =
    useAccountabilityCommunicationMessageSampleSizeLazyQuery({
      variables: prepareVariables(selectedSampleSizeType, formValues),
      fetchPolicy: 'network-only',
    });

  useEffect(() => {
    if (activeStep === CommunicationSteps.SampleSize) {
      loadSampleSize();
    }
  }, [activeStep, formValues, loadSampleSize]);

  const [
    loadAvailableFlows,
    { data: flowsData, loading: flowsLoading, error: flowsError },
  ] = useSurveyAvailableFlowsLazyQuery({
    fetchPolicy: 'network-only',
  });

  useEffect(() => {
    loadAvailableFlows();
  }, [loadAvailableFlows]);

  useEffect(() => {
    if (
      (flowsData?.surveyAvailableFlows === null || flowsError) &&
      !flowsLoading
    ) {
      navigate(`/error/${businessArea}`, {
        state: {
          errorMessage: t(
            'RapidPro is not set up in your country, please contact your Roll Out Focal Point',
          ),
          lastSuccessfulPage: `/${baseUrl}/accountability/communication`,
        },
      });
    }
  }, [flowsData, flowsError, flowsLoading, businessArea, baseUrl, navigate, t]);

  const validationSchema = useCallback(() => {
    const datum = {
      title: Yup.string(),
      body: Yup.string(),
    };

    if (activeStep === CommunicationSteps.Details) {
      datum.title = Yup.string()
        .min(4, t('Too short'))
        .max(60, t('Too long'))
        .required(t('Title is required'));
      datum.body = Yup.string()
        .min(4, t('Too short'))
        .max(1000, t('Too long'))
        .required(t('Message is required'));
    }
    setValidateData(true);

    return Yup.object().shape(datum);
  }, [activeStep, t]);

  const validate = (values): { error?: string } => {
    const { households, targetPopulation, registrationDataImport } = values;
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
  if (
    !hasPermissions(
      PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE,
      permissions,
    )
  )
    return <PermissionDenied />;

  const getSampleSizePercentage = (): string =>
    `(${getPercentage(
      sampleSizesData?.accountabilityCommunicationMessageSampleSize?.sampleSize,
      sampleSizesData?.accountabilityCommunicationMessageSampleSize
        ?.numberOfRecipients,
    )})`;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Communication'),
      to: `/${baseUrl}/accountability/communication`,
    },
  ];

  const handleNext = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
    setValidateData(false);
  };

  const handleBack = (values): void => {
    // Skip sample-size step when households are chosen
    if (values.households.length && activeStep === 2) {
      setActiveStep(0);
    } else {
      setActiveStep((prevActiveStep) => prevActiveStep - 1);
    }
  };

  const prepareMutationVariables = (
    values,
  ): CreateAccountabilityCommunicationMessageMutationVariables => ({
    input: {
      households: values.households,
      targetPopulation: values.targetPopulation,
      registrationDataImport: values.registrationDataImport,
      samplingType:
        selectedSampleSizeType === 0
          ? SamplingChoices.FullList
          : SamplingChoices.Random,
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
  });

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
      onSubmit={(values) => {
        if (activeStep === steps.length - 1) {
          confirm({
            title: t('Confirmation'),
            content: t('Are you sure you want to send this message?'),
          }).then(async () => {
            try {
              const response = await mutate({
                variables: prepareMutationVariables(values),
              });
              showMessage(t('Communication Ticket created.'));
              navigate(
                `/${baseUrl}/accountability/communication/${response.data.createAccountabilityCommunicationMessage.message.id}`,
              );
            } catch (e) {
              e.graphQLErrors.map((x) => showMessage(x.message));
            }
          });
        } else {
          handleNext();
        }
      }}
    >
      {({ submitForm, setValues, values, setFieldValue, errors }) => (
        <>
          <PageHeader
            title="New Message"
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
              <FormikEffect
                values={values}
                onChange={() => setFormValues(values)}
              />
              {activeStep === CommunicationSteps.LookUp && (
                <Box display="flex" flexDirection="column">
                  <LookUpSelectionCommunication
                    businessArea={businessArea}
                    values={values}
                    onValueChange={setFieldValue}
                    setValues={setValues}
                    selectedTab={selectedTab}
                    setSelectedTab={setSelectedTab}
                  />
                </Box>
              )}
              {activeStep === CommunicationSteps.SampleSize &&
                (values.households.length ? (
                  <Box px={8}>
                    <Box pt={3}>
                      <Box fontSize={12} color="#797979">
                        {t(
                          'You have selected households as the recipients group',
                        )}
                      </Box>
                      <Box
                        pb={3}
                        pt={3}
                        fontSize={16}
                        fontWeight="fontWeightBold"
                      >
                        {t('Message will be sent to all households selected')}:
                        ({values.households.length})
                      </Box>
                    </Box>
                  </Box>
                ) : (
                  <Box px={8}>
                    <Box display="flex" alignItems="center">
                      <Box pl={5} pr={5} fontWeight="500" fontSize="medium">
                        {t('Sample Size')}:
                      </Box>
                      <RadioGroup
                        aria-labelledby="selection-radio-buttons-group"
                        value={selectedSampleSizeType}
                        row
                        name="radio-buttons-group"
                      >
                        {SampleSizeTabs.map((tab, index) => (
                          <FormControlLabel
                            value={index}
                            onChange={() => {
                              setFormValues(values);
                              setSelectedSampleSizeType(index);
                            }}
                            key={tab}
                            control={<Radio color="primary" />}
                            label={tab}
                          />
                        ))}
                      </RadioGroup>
                    </Box>
                    <TabPanel value={selectedSampleSizeType} index={0}>
                      {mappedAdminAreas && (
                        <Field
                          name="excludedAdminAreasFull"
                          choices={mappedAdminAreas}
                          variant="outlined"
                          label={t('Filter Out Administrative Level Areas')}
                          component={FormikMultiSelectField}
                        />
                      )}
                      <Box pt={3}>
                        <Box
                          pb={3}
                          pt={3}
                          fontSize={16}
                          fontWeight="fontWeightBold"
                        >
                          Sample size:{' '}
                          {
                            sampleSizesData
                              ?.accountabilityCommunicationMessageSampleSize
                              ?.sampleSize
                          }{' '}
                          out of{' '}
                          {
                            sampleSizesData
                              ?.accountabilityCommunicationMessageSampleSize
                              ?.numberOfRecipients
                          }{' '}
                          {getSampleSizePercentage()}
                        </Box>
                      </Box>
                    </TabPanel>
                    <TabPanel value={selectedSampleSizeType} index={1}>
                      <Box pt={3}>
                        <Field
                          name="confidenceInterval"
                          label={t('Confidence Interval')}
                          min={90}
                          max={99}
                          component={FormikSliderField}
                          suffix="%"
                        />
                        <Field
                          name="marginOfError"
                          label={t('Margin of Error')}
                          min={0}
                          max={9}
                          component={FormikSliderField}
                          suffix="%"
                        />
                        <Typography variant="caption">
                          {t('Cluster Filters')}
                        </Typography>
                        <Box flexDirection="column" display="flex">
                          <Box display="flex">
                            <Field
                              name="adminCheckbox"
                              label={t('Administrative Level')}
                              component={FormikCheckboxField}
                            />
                            <Field
                              name="ageCheckbox"
                              label={t('Age of HoH')}
                              component={FormikCheckboxField}
                            />
                            <Field
                              name="sexCheckbox"
                              label={t('Gender of HoH')}
                              component={FormikCheckboxField}
                            />
                          </Box>
                          {values.adminCheckbox && (
                            <Field
                              name="excludedAdminAreasRandom"
                              choices={mappedAdminAreas}
                              variant="outlined"
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
                                      name="filterAgeMin"
                                      label={t('Minimum Age')}
                                      type="number"
                                      color="primary"
                                      component={FormikTextField}
                                    />
                                  </Grid>
                                  <Grid item xs={4}>
                                    <Field
                                      name="filterAgeMax"
                                      label={t('Maximum Age')}
                                      type="number"
                                      color="primary"
                                      component={FormikTextField}
                                    />
                                  </Grid>
                                </Grid>
                              </Grid>
                            )}
                            {values.sexCheckbox && (
                              <Grid item xs={5}>
                                <Field
                                  name="filterSex"
                                  label={t('Gender')}
                                  color="primary"
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
                          fontWeight="fontWeightBold"
                        >
                          Sample size:{' '}
                          {
                            sampleSizesData
                              ?.accountabilityCommunicationMessageSampleSize
                              ?.sampleSize
                          }{' '}
                          out of{' '}
                          {
                            sampleSizesData
                              ?.accountabilityCommunicationMessageSampleSize
                              ?.numberOfRecipients
                          }{' '}
                          {getSampleSizePercentage()}
                        </Box>
                      </Box>
                    </TabPanel>
                  </Box>
                ))}
              {activeStep === CommunicationSteps.Details && (
                <>
                  <Border />
                  <Box my={3}>
                    <Grid item xs={12}>
                      <Field
                        name="title"
                        required
                        fullWidth
                        variant="outlined"
                        label={t('Title')}
                        component={FormikTextField}
                        data-cy="input-title"
                      />
                    </Grid>
                  </Box>
                  <Grid item xs={12}>
                    <Field
                      name="body"
                      required
                      multiline
                      fullWidth
                      variant="outlined"
                      label={t('Message')}
                      component={FormikTextField}
                      data-cy="input-body"
                    />
                  </Grid>
                </>
              )}
              {dataChangeErrors(errors)}
            </Form>
            <Box pt={3} display="flex" flexDirection="row">
              <Box mr={3}>
                <Button
                  component={Link}
                  to={`/${baseUrl}/accountability/communication`}
                  data-cy="button-cancel"
                >
                  {t('Cancel')}
                </Button>
              </Box>
              <Box display="flex" ml="auto">
                <Button
                  disabled={activeStep === CommunicationSteps.LookUp}
                  onClick={() => handleBack(values)}
                  data-cy="button-back"
                >
                  {t('Back')}
                </Button>
                <LoadingButton
                  loading={loading}
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  data-cy="button-submit"
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
};
