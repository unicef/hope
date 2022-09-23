import {
  Box,
  Button,
  Grid,
  Step,
  StepLabel,
  Stepper,
  Typography,
} from '@material-ui/core';
import { Field, Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import { HouseholdQuestionnaire } from '../../../../components/accountability/Feedback/HouseholdQuestionnaire/HouseholdQuestionnaire';
import { IndividualQuestionnaire } from '../../../../components/accountability/Feedback/IndividualQuestionnnaire/IndividualQuestionnaire';
import { BreadCrumbsItem } from '../../../../components/core/BreadCrumbs';
import { ContainerColumnWithBorder } from '../../../../components/core/ContainerColumnWithBorder';
import { LabelizedField } from '../../../../components/core/LabelizedField';
import { LoadingButton } from '../../../../components/core/LoadingButton';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { OverviewContainer } from '../../../../components/core/OverviewContainer';
import { PageHeader } from '../../../../components/core/PageHeader';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { Consent } from '../../../../components/grievances/Consent';
import { LookUpHouseholdIndividualSelection } from '../../../../components/grievances/LookUps/LookUpHouseholdIndividual/LookUpHouseholdIndividualSelection';
import { LookUpRelatedTickets } from '../../../../components/grievances/LookUps/LookUpRelatedTickets/LookUpRelatedTickets';
import { prepareVariables } from '../../../../components/grievances/utils/createGrievanceUtils';

import {
  hasPermissionInModule,
  hasPermissions,
  PERMISSIONS,
} from '../../../../config/permissions';
import { useArrayToDict } from '../../../../hooks/useArrayToDict';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { usePermissions } from '../../../../hooks/usePermissions';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { FormikAdminAreaAutocomplete } from '../../../../shared/Formik/FormikAdminAreaAutocomplete';
import { FormikCheckboxField } from '../../../../shared/Formik/FormikCheckboxField';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';
import { FeedbackSteps } from '../../../../utils/constants';
import {
  useAllProgramsQuery,
  useAllUsersQuery,
  useGrievancesChoiceDataQuery,
} from '../../../../__generated__/graphql';

const steps = [
  'Category Selection',
  'Household/Individual Look up',
  'Identity Verification',
  'Description',
];

const BoxPadding = styled.div`
  padding: 15px 0;
`;
const NoRootPadding = styled.div`
  .MuiStepper-root {
    padding: 0 !important;
  }
`;
const InnerBoxPadding = styled.div`
  .MuiPaper-root {
    padding: 32px 20px;
  }
`;
const NewTicket = styled.div`
  padding: 20px;
`;
const BoxWithBorderBottom = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;
const BoxWithBorders = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

export const validationSchemaWithSteps = (currentStep: number): unknown => {
  const datum = {
    category: Yup.string()
      .required('Category is required')
      .nullable(),
    issueType: Yup.string()
      .required('Issue Type is required')
      .nullable(),
    admin: Yup.string().nullable(),
    description: Yup.string(),
    consent: Yup.bool(),
    area: Yup.string(),
    language: Yup.string(),
    selectedPaymentRecords: Yup.array()
      .of(Yup.string())
      .nullable(),
    selectedRelatedTickets: Yup.array()
      .of(Yup.string())
      .nullable(),
  };
  if (currentStep === FeedbackSteps.Description) {
    datum.description = Yup.string().required('Description is required');
  }
  if (currentStep >= FeedbackSteps.Verification) {
    datum.consent = Yup.bool().oneOf([true], 'Consent is required');
  }
  return Yup.object().shape(datum);
};

export function validateUsingSteps(
  values,
  activeStep,
  setValidateData,
): { [key: string]: string | { [key: string]: string } } {
  const errors: { [key: string]: string | { [key: string]: string } } = {};
  const verficationStepFields = [
    'size',
    'maleChildrenCount',
    'femaleChildrenCount',
    'childrenDisabledCount',
    'headOfHousehold',
    'countryOrigin',
    'address',
    'village',
    'admin1',
    'unhcrId',
    'months_displaced_h_f',
    'fullName',
    'birthDate',
    'phoneNo',
    'relationship',
  ];

  if (activeStep === FeedbackSteps.Lookup && !values.selectedHousehold) {
    errors.selectedHousehold = 'Household is Required';
  }

  if (activeStep === FeedbackSteps.Lookup) {
    if (!values.selectedIndividual) {
      errors.selectedIndividual = 'Individual is Required';
    } else if (!values.selectedHousehold) {
      errors.selectedHousehold = 'Household is Required';
    }
  }
  if (
    activeStep === FeedbackSteps.Verification &&
    (values.selectedHousehold ||
      (values.selectedIndividual && !values.verificationRequired))
  ) {
    if (
      verficationStepFields.filter((item) => values[item] === true).length < 5
    ) {
      setValidateData(true);
      errors.verificationRequired = 'Select correctly minimum 5 questions';
    }
  }
  return errors;
}

export const CreateFeedbackPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();

  const [activeStep, setActiveStep] = useState(FeedbackSteps.Selection);
  const [validateData, setValidateData] = useState(false);

  const initialValues = {
    category: null,
    issueType: null,
    selectedHousehold: null,
    selectedIndividual: null,
    description: '',
    language: '',
    consent: false,
    admin: null,
    area: '',
    selectedPaymentRecords: [],
    selectedRelatedTickets: [],
    identityVerified: false,
    priority: 3,
    urgency: 3,
    subCategory: null,
    partner: null,
    programme: null,
    comments: null,
  };
  const { data: userData, loading: userDataLoading } = useAllUsersQuery({
    variables: { businessArea, first: 1000 },
  });

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();

  const [mutate, { loading }] = useCreateFeedbackMutation();

  const issueTypeDict = useArrayToDict(
    choicesData?.grievanceTicketIssueTypeChoices,
    'category',
    '*',
  );

  const {
    data: allProgramsData,
    loading: loadingPrograms,
  } = useAllProgramsQuery({
    variables: { businessArea, status: ['ACTIVE'] },
    fetchPolicy: 'cache-and-network',
  });

  const allProgramsEdges = allProgramsData?.allPrograms?.edges || [];
  const mappedPrograms = allProgramsEdges.map((edge) => ({
    name: edge.node?.name,
    value: edge.node.id,
  }));

  if (userDataLoading || choicesLoading || loadingPrograms)
    return <LoadingComponent />;
  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.GRIEVANCES_CREATE, permissions))
    return <PermissionDenied />;

  if (!choicesData || !userData) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Feedback'),
      to: `/${businessArea}/accountability/feedback/`,
    },
  ];

  const handleNext = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        if (activeStep === steps.length - 1) {
          try {
            const response = await mutate(
              prepareVariables(businessArea, values),
            );
            showMessage(t('Feedback created.'), {
              pathname: `/${businessArea}/accountability/feedback/${response.data.createFeedback.feedback[0].id}`,
              historyMethod: 'push',
            });
          } catch (e) {
            e.graphQLErrors.map((x) => showMessage(x.message));
          }
        } else {
          setValidateData(false);
          handleNext();
        }
      }}
      validateOnChange={activeStep < FeedbackSteps.Verification || validateData}
      validateOnBlur={activeStep < FeedbackSteps.Verification || validateData}
      validationSchema={validationSchemaWithSteps(activeStep)}
      validate={(values) =>
        validateUsingSteps(
          values,

          activeStep,
          setValidateData,
        )
      }
    >
      {({ submitForm, values, setFieldValue, errors, touched }) => {
        return (
          <>
            <PageHeader
              title='New Feedback'
              breadCrumbs={
                hasPermissionInModule('FEEDBACK_VIEW_LIST', permissions)
                  ? breadCrumbsItems
                  : null
              }
            />
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <NewTicket>
                  <InnerBoxPadding>
                    <ContainerColumnWithBorder>
                      <NoRootPadding>
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
                      </NoRootPadding>
                      {activeStep === FeedbackSteps.Selection && (
                        <Grid container spacing={3}>
                          <Grid item xs={6}>
                            <LabelizedField label={t('Category')}>
                              {t('Feedback')}
                            </LabelizedField>
                          </Grid>
                          <Grid item xs={6}>
                            <Field
                              name='issueType'
                              label='Issue Type'
                              variant='outlined'
                              required
                              choices={
                                issueTypeDict[values.category].subCategories
                              }
                              component={FormikSelectField}
                            />
                          </Grid>
                        </Grid>
                      )}
                      {activeStep === FeedbackSteps.Lookup && (
                        <BoxWithBorders>
                          <Box display='flex' flexDirection='column'>
                            <LookUpHouseholdIndividualSelection
                              values={values}
                              onValueChange={setFieldValue}
                              errors={errors}
                              touched={touched}
                            />
                          </Box>
                        </BoxWithBorders>
                      )}
                      {activeStep === FeedbackSteps.Verification && (
                        <BoxWithBorders>
                          {values.selectedHousehold && (
                            <>
                              <Typography variant='subtitle1'>
                                {t(
                                  'Select correctly answered questions (minimum 5)',
                                )}
                              </Typography>
                              <Box py={4}>
                                <Typography variant='subtitle2'>
                                  {t('Household Questionnaire')}
                                </Typography>
                                <Box py={4}>
                                  <HouseholdQuestionnaire values={values} />
                                </Box>
                              </Box>
                              <Typography variant='subtitle2'>
                                {t('Individual Questionnaire')}
                              </Typography>
                              <Box py={4}>
                                <IndividualQuestionnaire values={values} />
                              </Box>
                              <BoxWithBorderBottom />
                            </>
                          )}
                          <Consent />
                          <Field
                            name='consent'
                            label={t('Received Consent')}
                            color='primary'
                            fullWidth
                            required
                            container={false}
                            component={FormikCheckboxField}
                          />
                        </BoxWithBorders>
                      )}
                      {activeStep === steps.length - 1 && (
                        <BoxPadding>
                          <OverviewContainer>
                            <Grid container spacing={6}>
                              <LabelizedField label={t('Category')}>
                                {t('Feedback')}
                              </LabelizedField>
                            </Grid>
                          </OverviewContainer>
                          <BoxWithBorderBottom />
                          <BoxPadding />
                          <Grid container spacing={3}>
                            <Grid item xs={12}>
                              <Field
                                name='description'
                                multiline
                                fullWidth
                                variant='outlined'
                                label={t('Description')}
                                required
                                component={FormikTextField}
                              />
                            </Grid>
                            <Grid item xs={12}>
                              <Field
                                name='comments'
                                multiline
                                fullWidth
                                variant='outlined'
                                label={t('Comments')}
                                component={FormikTextField}
                              />
                            </Grid>
                            <Grid item xs={6}>
                              <Field
                                name='admin'
                                label={t('Administrative Level 2')}
                                variant='outlined'
                                component={FormikAdminAreaAutocomplete}
                              />
                            </Grid>
                            <Grid item xs={6}>
                              <Field
                                name='area'
                                fullWidth
                                variant='outlined'
                                label={t('Area / Village / Pay point')}
                                component={FormikTextField}
                              />
                            </Grid>
                            <Grid item xs={6}>
                              <Field
                                name='language'
                                multiline
                                fullWidth
                                variant='outlined'
                                label={t('Languages Spoken')}
                                component={FormikTextField}
                              />
                            </Grid>
                            <Grid item xs={6}>
                              <Field
                                name='programme'
                                fullWidth
                                variant='outlined'
                                label={t('Programme Title')}
                                choices={mappedPrograms}
                                component={FormikSelectField}
                              />
                            </Grid>
                          </Grid>
                          <Box pt={5}>
                            <BoxWithBorders>
                              <Grid container spacing={4}>
                                <Grid item xs={6}>
                                  <Box py={3}>
                                    <LookUpRelatedTickets
                                      values={values}
                                      onValueChange={setFieldValue}
                                    />
                                  </Box>
                                </Grid>
                              </Grid>
                            </BoxWithBorders>
                          </Box>
                        </BoxPadding>
                      )}
                      <Box pt={3} display='flex' flexDirection='row'>
                        <Box mr={3}>
                          <Button
                            component={Link}
                            to={`/${businessArea}/accountability/feedback`}
                          >
                            {t('Cancel')}
                          </Button>
                        </Box>
                        <Box display='flex' ml='auto'>
                          <Button
                            disabled={activeStep === 0}
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
                            {activeStep === steps.length - 1
                              ? t('Save')
                              : t('Next')}
                          </LoadingButton>
                        </Box>
                      </Box>
                    </ContainerColumnWithBorder>
                  </InnerBoxPadding>
                </NewTicket>
              </Grid>
            </Grid>
          </>
        );
      }}
    </Formik>
  );
};
