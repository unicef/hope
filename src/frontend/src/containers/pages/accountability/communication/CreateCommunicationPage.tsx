import { LookUpSelectionCommunication } from '@components/accountability/Communication/LookUpsCommunication/LookUpSelectionCommunication';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { useConfirmation } from '@components/core/ConfirmationDialog';
import { FormikEffect } from '@components/core/FormikEffect';
import { LoadingButton } from '@components/core/LoadingButton';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TabPanel } from '@components/core/TabPanel';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaperContainer } from '@components/targeting/PaperContainer';
import { useMutation, useQuery } from '@tanstack/react-query';
import { MessageCreate } from '@restgenerated/models/MessageCreate';
import { SamplingTypeE86Enum } from '@restgenerated/models/SamplingTypeE86Enum';
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
import { MessageSampleSize } from '@restgenerated/models/MessageSampleSize';
import { RestService } from '@restgenerated/services/RestService';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { FormikMultiSelectField } from '@shared/Formik/FormikMultiSelectField';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikSliderField } from '@shared/Formik/FormikSliderField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { CommunicationSteps, CommunicationTabsValues } from '@utils/constants';
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
  samplingType: SamplingTypeE86Enum.FULL_LIST,
};

function prepareSampleSizeRequest(
  selectedSampleSizeType,
  values,
): MessageSampleSize {
  const samplingType =
    selectedSampleSizeType === 0
      ? SamplingTypeE86Enum.FULL_LIST
      : SamplingTypeE86Enum.RANDOM;

  const fullListArguments = {
    excludedAdminAreas: values.excludedAdminAreasFull || [],
  };

  const randomSamplingArguments = {
    confidenceInterval: values.confidenceInterval * 0.01,
    marginOfError: values.marginOfError * 0.01,
    excludedAdminAreas: values.adminCheckbox
      ? values.excludedAdminAreasRandom
      : [],
    age: values.ageCheckbox
      ? { min: values.filterAgeMin, max: values.filterAgeMax }
      : null,
    sex: values.sexCheckbox ? values.filterSex : null,
  };

  return {
    households: values.households,
    paymentPlan: values.targetPopulation,
    registrationDataImport: values.registrationDataImport,
    samplingType,
    // Always include both arguments but set them appropriately based on sampling type
    fullListArguments:
      samplingType === SamplingTypeE86Enum.FULL_LIST ? fullListArguments : null,
    randomSamplingArguments:
      samplingType === SamplingTypeE86Enum.RANDOM
        ? randomSamplingArguments
        : null,
  };
}

const CreateCommunicationPage = (): ReactElement => {
  const { t } = useTranslation();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const { mutateAsync: mutate, isPending: loading } = useMutation({
    mutationFn: (data: MessageCreate) =>
      RestService.restBusinessAreasProgramsMessagesCreate({
        businessAreaSlug: businessArea,
        programSlug: programId,
        requestBody: data,
      }),
  });
  const { showMessage } = useSnackbar();
  const navigate = useNavigate();
  const permissions = usePermissions();
  const confirm = useConfirmation();

  const [activeStep, setActiveStep] = useState(CommunicationSteps.LookUp);
  const [selectedTab, setSelectedTab] = useState(
    CommunicationTabsValues.HOUSEHOLD,
  );
  const [selectedSampleSizeType, setSelectedSampleSizeType] = useState(0);
  const [formValues, setFormValues] = useState(initialValues);
  const [validateData, setValidateData] = useState(false);

  const [sampleSizesData, setSampleSizesData] = useState<any>(null);
  const [sampleSizeLoading, setSampleSizeLoading] = useState<boolean>(false);
  const [sampleSizeError, setSampleSizeError] = useState<Error | null>(null);

  const { data: adminAreasData } = useQuery<PaginatedAreaList>({
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

  const loadSampleSize = useCallback(async () => {
    if (!businessArea) return;

    try {
      setSampleSizeLoading(true);
      setSampleSizeError(null);

      const requestBody = prepareSampleSizeRequest(
        selectedSampleSizeType,
        formValues,
      );
      const result =
        await RestService.restBusinessAreasProgramsMessagesSampleSizeCreate({
          businessAreaSlug: businessArea,
          programSlug: programId,
          requestBody,
        });

      // The API response has a different shape than the request type
      // Use type assertion to access the properties we need
      const response = result as unknown as {
        sampleSize?: number;
        numberOfRecipients?: number;
      };

      setSampleSizesData({
        accountabilityCommunicationMessageSampleSize: {
          sampleSize: response.sampleSize || 0,
          numberOfRecipients: response.numberOfRecipients || 0,
        },
      });
    } catch (error) {
      console.error('Error loading sample size data:', error);
      setSampleSizeError(error as Error);
    } finally {
      setSampleSizeLoading(false);
    }
  }, [businessArea, selectedSampleSizeType, formValues, programId]);

  useEffect(() => {
    if (activeStep === CommunicationSteps.SampleSize) {
      loadSampleSize();
    }
  }, [activeStep, formValues, loadSampleSize]);

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
    } catch (error) {
      console.error('Error loading available flows:', error);
      setFlowsError(error);
    } finally {
      setFlowsLoading(false);
    }
  }, [businessArea, programId]);

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

  const mappedAdminAreas = adminAreasData?.results?.length
    ? adminAreasData.results.map((area) => ({
        value: area.id,
        name: area.name || '',
      }))
    : [];

  if (permissions === null || permissions.length === 0) return null;

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
    if (values.households.length && activeStep === 2) {
      setActiveStep(0);
    } else {
      setActiveStep((prevActiveStep) => prevActiveStep - 1);
    }
  };

  const prepareMutationVariables = (values): MessageCreate => ({
    title: values.title,
    body: values.body,
    households: values.households,
    paymentPlan: values.targetPopulation,
    registrationDataImport: values.registrationDataImport,
    samplingType:
      selectedSampleSizeType === 0
        ? SamplingTypeE86Enum.FULL_LIST
        : SamplingTypeE86Enum.RANDOM,
    fullListArguments:
      selectedSampleSizeType === 0
        ? {
            excludedAdminAreas: values.excludedAdminAreasFull || [],
          }
        : null,
    randomSamplingArguments:
      selectedSampleSizeType === 1
        ? {
            excludedAdminAreas: values.excludedAdminAreasRandom || [],
            confidenceInterval: values.confidenceInterval * 0.01,
            marginOfError: values.marginOfError * 0.01,
            age: values.ageCheckbox
              ? { min: values.filterAgeMin, max: values.filterAgeMax }
              : null,
            sex: values.sexCheckbox ? values.filterSex : null,
          }
        : null,
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
              const response = await mutate(prepareMutationVariables(values));
              showMessage(t('Communication Ticket created.'));
              navigate(
                `/${baseUrl}/accountability/communication/${response.id}`,
              );
            } catch (e) {
              showMessage(e.message || t('An error occurred'));
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
            <Grid size={{ xs: 9 }}>
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
                      {sampleSizeError && (
                        <Box mb={3}>
                          <Typography color="error">
                            {t('Error loading sample size data')}:{' '}
                            {sampleSizeError.message}
                          </Typography>
                        </Box>
                      )}
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
                            </>
                          )}
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
                            </>
                          )}
                        </Box>
                      </Box>
                    </TabPanel>
                  </Box>
                ))}
              {activeStep === CommunicationSteps.Details && (
                <>
                  <Border />
                  <Box my={3}>
                    <Grid size={{ xs: 12 }}>
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
                  <Grid size={{ xs: 12 }}>
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

export default withErrorBoundary(
  CreateCommunicationPage,
  'CreateCommunicationPage',
);
