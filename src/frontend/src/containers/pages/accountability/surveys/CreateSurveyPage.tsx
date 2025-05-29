import { LookUpSelectionSurveys } from '@components/accountability/Surveys/LookUpsSurveys/LookUpSelectionSurveys';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { useConfirmation } from '@components/core/ConfirmationDialog';
import { FormikEffect } from '@components/core/FormikEffect';
import { LoadingButton } from '@components/core/LoadingButton';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TabPanel } from '@components/core/TabPanel';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaperContainer } from '@components/targeting/PaperContainer';
import {
  CreateSurveyAccountabilityMutationVariables,
  SamplingChoices,
  SurveyCategory,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  FormControlLabel,
  FormHelperText,
  Grid2 as Grid,
  Radio,
  RadioGroup,
  Step,
  StepLabel,
  Stepper,
  Typography,
} from '@mui/material';
import { PaginatedAreaList } from '@restgenerated/models/PaginatedAreaList';
import { SurveySampleSize } from '@restgenerated/models/SurveySampleSize';
import { SurveySampleSizeSamplingTypeEnum } from '@restgenerated/models/SurveySampleSizeSamplingTypeEnum';
import { RestService } from '@restgenerated/services/RestService';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { FormikMultiSelectField } from '@shared/Formik/FormikMultiSelectField';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikSliderField } from '@shared/Formik/FormikSliderField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useMutation, useQuery } from '@tanstack/react-query';
import { SurveySteps, SurveyTabsValues } from '@utils/constants';
import { getPercentage } from '@utils/utils';
import { Field, Form, Formik } from 'formik';
import {
  ReactElement,
  ReactNode,
  useCallback,
  useEffect,
  useState,
} from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';

const steps = ['Recipients Look up', 'Sample Size', 'Details'];
const sampleSizeTabs = ['Full List', 'Random Sampling'];

const Border = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

function prepareSampleSizeRequest(selectedSampleSizeType, values) {
  return {
    value: values.program,
    paymentPlan: values.targetPopulation,
    samplingType:
      selectedSampleSizeType === 0
        ? SurveySampleSizeSamplingTypeEnum.FULL_LIST
        : SurveySampleSizeSamplingTypeEnum.RANDOM,
    fullListArguments:
      selectedSampleSizeType === 0
        ? {
            excludedAdminAreas: values.excludedAdminAreasFull || [],
          }
        : undefined,
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
        : undefined,
  };
}

const CreateSurveyPage = (): ReactElement => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { mutateAsync: mutate, isPending: loading } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      programSlug,
      requestBody,
    }: {
      businessAreaSlug: string;
      programSlug: string;
      requestBody: any;
    }) =>
      RestService.restBusinessAreasProgramsSurveysCreate({
        businessAreaSlug,
        programSlug,
        requestBody,
      }),
  });
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const permissions = usePermissions();
  const confirm = useConfirmation();
  const { pathname } = location;
  const parts = pathname.split('/');
  const categoryIndex = parts.indexOf('create') + 1;
  const categoryFromUrl = parts[categoryIndex];
  const isCategoryValid = [
    SurveyCategory.Sms,
    SurveyCategory.Manual,
    SurveyCategory.RapidPro,
  ].includes(categoryFromUrl as SurveyCategory);
  const [category, setCategory] = useState<string | undefined>(categoryFromUrl);
  useEffect(() => {
    setCategory(categoryFromUrl);
  }, [category, pathname, categoryFromUrl]);

  // Set category to SMS if the user types random string in url
  if (!isCategoryValid) {
    navigate(
      `/${businessArea}/accountability/surveys/create/${SurveyCategory.Sms}`,
    );
  }
  const initialValues = {
    category,
    message: '',
    program: programId,
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
    samplingType: SamplingChoices.FullList,
  };

  const [activeStep, setActiveStep] = useState(SurveySteps.LookUp);
  const [selectedTab, setSelectedTab] = useState(SurveyTabsValues.PROGRAM);
  const [selectedSampleSizeType, setSelectedSampleSizeType] = useState(0);
  const [formValues, setFormValues] = useState(initialValues);
  const [validateData, setValidateData] = useState(false);

  const { data: adminAreasData, isLoading: adminAreasLoading } =
    useQuery<PaginatedAreaList>({
      queryKey: ['adminAreas', businessArea, { areaTypeAreaLevel: 2 }],
      queryFn: async () => {
        return RestService.restAreasList({
          limit: 100,
          areaTypeAreaLevel: 2,
          search: undefined,
        });
      },
      enabled: !!businessArea,
    });

  const [sampleSizesData, setSampleSizesData] = useState<any>(null);
  const [sampleSizeLoading, setSampleSizeLoading] = useState<boolean>(false);
  const [sampleSizeError, setSampleSizeError] = useState<Error | null>(null);

  const loadSampleSize = useCallback(async () => {
    if (!businessArea || !programId) return;

    try {
      setSampleSizeLoading(true);
      setSampleSizeError(null);

      const requestBody = prepareSampleSizeRequest(
        selectedSampleSizeType,
        formValues,
      );

      const result =
        await RestService.restBusinessAreasProgramsSurveysSampleSizeCreate({
          businessAreaSlug: businessArea,
          programSlug: programId,
          requestBody,
        });

      setSampleSizesData(result);
    } catch (error) {
      console.error('Error loading sample size data:', error);
      setSampleSizeError(error as Error);
    } finally {
      setSampleSizeLoading(false);
    }
  }, [businessArea, programId, selectedSampleSizeType, formValues]);

  const [flowsData, setFlowsData] = useState(null);
  const [flowsLoading, setFlowsLoading] = useState(false);
  const [flowsError, setFlowsError] = useState(null);

  const loadAvailableFlows = useCallback(async () => {
    if (!businessArea || !programId) return;

    try {
      setFlowsLoading(true);
      const result =
        await RestService.restBusinessAreasProgramsSurveysAvailableFlowsList({
          businessAreaSlug: businessArea,
          programSlug: programId,
        });
      setFlowsData({ surveyAvailableFlows: result });
      console.log('Available flows loaded:', result);
    } catch (error) {
      console.error('Error loading available flows:', error);
      setFlowsError(error);
    } finally {
      setFlowsLoading(false);
    }
  }, [businessArea, programId]);

  useEffect(() => {
    if (category === SurveyCategory.RapidPro) {
      loadAvailableFlows();
    }
  }, [category, loadAvailableFlows]);

  useEffect(() => {
    if (activeStep === SurveySteps.SampleSize) {
      loadSampleSize();
    }
  }, [activeStep, formValues, loadSampleSize]);

  const validationSchema = useCallback(() => {
    const datum = {
      title: Yup.string(),
      body: Yup.string(),
    };
    if (activeStep === SurveySteps.Details) {
      datum.title = Yup.string()
        .min(4, t('Too short'))
        .max(255, t('Too long'))
        .required(t('Title is required'));
      if (category === 'SMS') {
        datum.body = Yup.string()
          .min(4, t('Too short'))
          .max(255, t('Too long'))
          .required(t('Message is required'));
      }
    }
    setValidateData(true);

    return Yup.object().shape(datum);
  }, [activeStep, t, category]);

  useEffect(() => {
    // Redirect to error page if no flows available
    if (
      (flowsData?.surveyAvailableFlows === null || flowsError) &&
      !flowsLoading
    ) {
      navigate(`/error/${businessArea}`, {
        state: {
          errorMessage: t(
            'RapidPro is not set up in your country, please contact your Roll Out Focal Point',
          ),
          lastSuccessfulPage: `/${baseUrl}/accountability/surveys`,
        },
      });
    }
  }, [
    flowsData,
    category,
    businessArea,
    navigate,
    t,
    baseUrl,
    flowsError,
    flowsLoading,
  ]);

  if (permissions === null || !adminAreasData) return null;
  if (
    !hasPermissions(PERMISSIONS.ACCOUNTABILITY_SURVEY_VIEW_CREATE, permissions)
  )
    return <PermissionDenied />;

  if (adminAreasLoading || flowsLoading) return <LoadingComponent />;

  const validate = (values): { error?: string } => {
    const { program, targetPopulation } = values;
    const errors: { [key: string]: string | { [key: string]: string } } = {};
    if (!targetPopulation && !program) {
      errors.error = t('Field Selection is required');
    }
    return errors;
  };

  const mappedAdminAreas = adminAreasData?.results?.length
    ? adminAreasData.results.map((area) => ({
        value: area.id,
        name: area.name || '',
      }))
    : [];

  const mappedFlows = flowsData?.surveyAvailableFlows?.length
    ? flowsData.surveyAvailableFlows.map((el) => ({
        value: el.id,
        name: el.name,
      }))
    : [];

  const getSampleSizePercentage = (): string => {
    if (!sampleSizesData) return '(0%)';

    const sampleSizeValue =
      sampleSizesData.sample_size ||
      sampleSizesData.sampleSize ||
      sampleSizesData.numberOfSamples ||
      0;

    const totalRecipients =
      sampleSizesData.number_of_recipients ||
      sampleSizesData.numberOfRecipients ||
      sampleSizesData.total ||
      0;

    return `(${getPercentage(sampleSizeValue, totalRecipients)})`;
  };

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Surveys'),
      to: `/${baseUrl}/accountability/surveys`,
    },
  ];

  const handleNext = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
    setValidateData(false);
  };

  const handleBack = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const matchTitle = (values): string =>
    category === SurveyCategory.Sms || category === SurveyCategory.Manual
      ? values.title
      : flowsData?.surveyAvailableFlows.find((el) => values.title === el.id).id;

  const prepareMutationVariables = (
    values,
  ): CreateSurveyAccountabilityMutationVariables => ({
    input: {
      title: matchTitle(values),
      body: values.body,
      category: values.category,
      paymentPlan: values.targetPopulation,
      program: values.program,
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
      flow: values.title,
    },
  });

  const dataChangeErrors = (errors): ReactElement[] =>
    ['error'].map((fieldname) => (
      <FormHelperText key={fieldname} error>
        {errors[fieldname]}
      </FormHelperText>
    ));

  const matchCategory = (surveyCategory): string => {
    switch (surveyCategory) {
      case SurveyCategory.Sms:
        return t('SMS');
      case SurveyCategory.RapidPro:
        return t('Rapid Pro');
      case SurveyCategory.Manual:
        return t('Manual');
      default:
        return '';
    }
  };

  return (
    <>
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
              content:
                category === SurveyCategory.Manual
                  ? t('Are you sure you want to save this survey?')
                  : t('Are you sure you want to send this survey?'),
              continueText:
                category === SurveyCategory.Manual ? t('Save') : t('Send'),
            }).then(async () => {
              try {
                const variables = prepareMutationVariables(values);
                const requestBody = {
                  title: variables.input.title,
                  body: variables.input.body,
                  category: variables.input.category,
                  paymentPlan: variables.input.paymentPlan,
                  program: variables.input.program,
                  samplingType: variables.input.samplingType,
                  fullListArguments: variables.input.fullListArguments,
                  randomSamplingArguments:
                    variables.input.randomSamplingArguments,
                  flow: variables.input.flow,
                };

                const response = await mutate({
                  businessAreaSlug: businessArea,
                  programSlug: programId,
                  requestBody,
                });
                showMessage(t('Survey created.'));
                navigate(`/${baseUrl}/accountability/surveys/${response.id}`);
              } catch (e) {
                showMessage(e.message || 'Error creating survey');
              }
            });
          } else {
            setFormValues(values);
            handleNext();
          }
        }}
      >
        {({ submitForm, setValues, values, setFieldValue, errors }) => (
          <>
            <PageHeader
              title={`${'New Survey'} > ${matchCategory(category)}`}
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
              <Grid size={{ xs: 12 }}>
                <Stepper activeStep={activeStep}>
                  {steps.map((label) => {
                    const stepProps: { completed?: boolean } = {};
                    const labelProps: {
                      optional?: ReactNode;
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
                  <Box display="flex" flexDirection="column">
                    <LookUpSelectionSurveys
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
                    {sampleSizeError && (
                      <Box mb={3}>
                        <Typography color="error">
                          {t('Error loading sample size data')}:{' '}
                          {sampleSizeError.message}
                        </Typography>
                      </Box>
                    )}
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
                        {sampleSizeTabs.map((tab, index) => (
                          <FormControlLabel
                            value={index}
                            data-cy={`radio-button-${tab}`}
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
                      <Box pt={6}>
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
                            {sampleSizeLoading ? (
                              <span>{t('Loading...')}</span>
                            ) : (
                              <>
                                {sampleSizesData?.sample_size ||
                                  sampleSizesData?.sampleSize ||
                                  sampleSizesData?.numberOfSamples ||
                                  0}{' '}
                                out of{' '}
                                {sampleSizesData?.number_of_recipients ||
                                  sampleSizesData?.numberOfRecipients ||
                                  sampleSizesData?.total ||
                                  0}{' '}
                                {getSampleSizePercentage()}
                              </>
                            )}
                          </Box>
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
                              <Grid size={{ xs: 12 }}>
                                <Grid container>
                                  <Grid size={{ xs: 4 }}>
                                    <Field
                                      name="filterAgeMin"
                                      label={t('Minimum Age')}
                                      type="number"
                                      color="primary"
                                      component={FormikTextField}
                                    />
                                  </Grid>
                                  <Grid size={{ xs: 4 }}>
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
                              <Grid size={{ xs: 5 }}>
                                <Field
                                  name="filterSex"
                                  label={t('Gender')}
                                  color="primary"
                                  choices={[
                                    { value: 'FEMALE', name: t('Female') },
                                    { value: 'MALE', name: t('Male') },
                                    { value: 'OTHER', name: t('Other') },
                                    {
                                      value: 'NOT_COLLECTED',
                                      name: t('Not Collected'),
                                    },
                                    {
                                      value: 'NOT_ANSWERED',
                                      name: t('Not Answered'),
                                    },
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
                          {sampleSizeLoading ? (
                            <span>{t('Loading...')}</span>
                          ) : (
                            <>
                              {sampleSizesData?.sample_size ||
                                sampleSizesData?.sampleSize ||
                                sampleSizesData?.numberOfSamples ||
                                0}{' '}
                              out of{' '}
                              {sampleSizesData?.number_of_recipients ||
                                sampleSizesData?.numberOfRecipients ||
                                sampleSizesData?.total ||
                                0}{' '}
                              {getSampleSizePercentage()}
                            </>
                          )}
                        </Box>
                      </Box>
                    </TabPanel>
                  </Box>
                )}
                {activeStep === SurveySteps.Details && (
                  <>
                    <Border />
                    <Box my={3}>
                      <Grid size={{ xs: 12 }}>
                        {category === SurveyCategory.RapidPro ? (
                          <Field
                            name="title"
                            label={t('Title')}
                            color="primary"
                            choices={mappedFlows}
                            component={FormikSelectField}
                            required
                            data-cy="input-title"
                          />
                        ) : (
                          <Field
                            name="title"
                            label={t('Title')}
                            fullWidth
                            required
                            variant="outlined"
                            component={FormikTextField}
                            data-cy="input-title"
                          />
                        )}
                      </Grid>
                    </Box>
                    {category === SurveyCategory.Sms && (
                      <Box my={3}>
                        <Grid size={{ xs: 12 }}>
                          <Field
                            name="body"
                            required
                            multiline
                            fullWidth
                            variant="outlined"
                            label={t('Message')}
                            component={FormikTextField}
                            data-cy="input-message"
                          />
                        </Grid>
                      </Box>
                    )}
                    <Grid size={{ xs: 12 }}>
                      <Box
                        pb={3}
                        pt={3}
                        fontSize={16}
                        fontWeight="fontWeightBold"
                      >
                        {t('Number of selected recipients')}:{' '}
                        {sampleSizeLoading ? (
                          <span>{t('Loading...')}</span>
                        ) : (
                          sampleSizesData?.sample_size ||
                          sampleSizesData?.sampleSize ||
                          sampleSizesData?.numberOfSamples ||
                          0
                        )}
                      </Box>
                    </Grid>
                  </>
                )}
                {dataChangeErrors(errors)}
              </Form>
              <Box pt={3} display="flex" flexDirection="row">
                <Box mr={3}>
                  <Button
                    component={Link}
                    data-cy="button-cancel"
                    to={`/${baseUrl}/accountability/surveys`}
                  >
                    {t('Cancel')}
                  </Button>
                </Box>
                <Box display="flex" ml="auto">
                  <Button
                    disabled={activeStep === SurveySteps.LookUp}
                    onClick={handleBack}
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
                    {t(
                      activeStep === steps.length - 1
                        ? t(
                            category === SurveyCategory.Manual
                              ? 'Save'
                              : 'Send',
                          )
                        : 'Next',
                    )}
                  </LoadingButton>
                </Box>
              </Box>
            </PaperContainer>
          </>
        )}
      </Formik>
    </>
  );
};

export default withErrorBoundary(CreateSurveyPage, 'CreateSurveyPage');
