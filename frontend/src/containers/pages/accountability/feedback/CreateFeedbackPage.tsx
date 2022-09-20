import {
  Box,
  Button,
  Grid,
  GridSize,
  Step,
  StepLabel,
  Stepper,
  Typography,
} from '@material-ui/core';
import { Field, Formik } from 'formik';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../../../components/core/BreadCrumbs';
import { ContainerColumnWithBorder } from '../../../../components/core/ContainerColumnWithBorder';
import { ContentLink } from '../../../../components/core/ContentLink';
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
import { validateUsingSteps } from '../../../../components/grievances/utils/validateGrievance';
import { validationSchemaWithSteps } from '../../../../components/grievances/utils/validationSchema';
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
import {
  FeedbackSteps,
  GRIEVANCE_ISSUE_TYPES,
} from '../../../../utils/constants';
import {
  useAllProgramsQuery,
  useAllUsersQuery,
  useGrievancesChoiceDataQuery,
  useUserChoiceDataQuery,
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

export const CreateFeedbackPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();

  const [activeStep, setActiveStep] = useState(FeedbackSteps.Selection);
  const [validateData, setValidateData] = useState(false);

  const initialValues = {
    description: '',
    category: null,
    language: '',
    consent: false,
    admin: null,
    area: '',
    selectedHousehold: null,
    selectedIndividual: null,
    selectedPaymentRecords: [],
    selectedRelatedTickets: [],
    identityVerified: false,
    issueType: null,
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

  const { data: userChoices } = useUserChoiceDataQuery();

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

  const hasCategorySelected = (values): boolean => {
    return !!values.category;
  };

  const hasHouseholdSelected = (values): boolean => {
    return !!values.selectedHousehold?.id;
  };

  const hasIndividualSelected = (values): boolean => {
    return !!values.selectedIndividual?.id;
  };

  const handleNext = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const selectedIssueType = (values): string => {
    return values.issueType
      ? choicesData.grievanceTicketIssueTypeChoices
          .filter((el) => el.category === values.category.toString())[0]
          .subCategories.filter(
            (el) => el.value === values.issueType.toString(),
          )[0].name
      : '-';
  };

  const showHouseholdQuestionnaire = (values): ReactElement => {
    const selectedHouseholdData = values.selectedHousehold;
    return (
      <Grid container spacing={6}>
        {[
          {
            name: 'size',
            label: t('Household Size'),
            value: selectedHouseholdData.size,
            size: 3,
          },
          {
            name: 'maleChildrenCount',
            label: t('Number of Male Children'),
            value: selectedHouseholdData.maleChildrenCount?.toString(),
            size: 3,
          },
          {
            name: 'femaleChildrenCount',
            label: t('Number of Female Children'),
            value: selectedHouseholdData.femaleChildrenCount?.toString(),
            size: 3,
          },
          {
            name: 'childrenDisabledCount',
            label: t('Number of Disabled Children'),
            value: selectedHouseholdData.childrenDisabledCount?.toString(),
            size: 3,
          },
          {
            name: 'headOfHousehold',
            label: t('Head of Household'),
            value: (
              <ContentLink
                href={`/${businessArea}/population/individuals/${selectedHouseholdData.headOfHousehold.id}`}
              >
                {selectedHouseholdData.headOfHousehold.fullName}
              </ContentLink>
            ),
            size: 3,
          },
          {
            name: 'countryOrigin',
            label: t('Country of Origin'),
            value: selectedHouseholdData.countryOrigin,
            size: 3,
          },
          {
            name: 'address',
            label: t('Address'),
            value: selectedHouseholdData.address,
            size: 3,
          },
          {
            name: 'village',
            label: t('Village'),
            value: selectedHouseholdData.village,
            size: 3,
          },
          {
            name: 'admin1',
            label: t('Administrative Level 1'),
            value: selectedHouseholdData.admin1?.name,
            size: 3,
          },
          {
            name: 'unhcrId',
            label: t('UNHCR CASE ID'),
            value: selectedHouseholdData.unicefId,
            size: 3,
          },
          {
            name: 'months_displaced_h_f',
            label: t('LENGTH OF TIME SINCE ARRIVAL'),
            value: selectedHouseholdData.flexFields?.months_displaced_h_f,
            size: 3,
          },
        ].map((el) => (
          <Grid item xs={3}>
            <Field
              name={el.name}
              label={el.label}
              displayValue={el.value || '-'}
              color='primary'
              component={FormikCheckboxField}
            />
          </Grid>
        ))}
      </Grid>
    );
  };

  const showIndividualQuestionnaire = (values): ReactElement => {
    const selectedIndividualData =
      values.selectedIndividual || values.selectedHousehold.headOfHousehold;
    return (
      <Grid container spacing={6}>
        {[
          {
            name: 'fullName',
            label: t('Individual Full Name'),
            value: (
              <ContentLink
                href={`/${businessArea}/population/individuals/${selectedIndividualData.id}`}
              >
                {selectedIndividualData.fullName}
              </ContentLink>
            ),
            size: 3,
          },
          {
            name: 'birthDate',
            label: t('Birth Date'),
            value: selectedIndividualData.birthDate,
            size: 3,
          },
          {
            name: 'phoneNo',
            label: t('Phone Number'),
            value: selectedIndividualData.phoneNo,
            size: 3,
          },
          {
            name: 'relationship',
            label: t('Relationship to HOH'),
            value: selectedIndividualData.relationship,
            size: 3,
          },
        ].map((el) => (
          <Grid item xs={3}>
            <Field
              name={el.name}
              label={el.label}
              displayValue={el.value || '-'}
              color='primary'
              component={FormikCheckboxField}
            />
          </Grid>
        ))}
      </Grid>
    );
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

            showMessage(t('Grievance Ticket created.'), {
              pathname: `/${businessArea}/grievance-and-feedback/${response.data.createGrievanceTicket.grievanceTickets[0].id}`,
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
      validate={(values) =>
        validateUsingSteps(
          values,
          allAddIndividualFieldsData,
          individualFieldsDict,
          householdFieldsDict,
          activeStep,
          setValidateData,
        )
      }
      validationSchema={validationSchemaWithSteps(activeStep)}
    >
      {({
        submitForm,
        values,
        setFieldValue,
        errors,
        touched,
        handleChange,
      }) => {
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
                              label='Issue Type*'
                              variant='outlined'
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
                                  {showHouseholdQuestionnaire(values)}
                                </Box>
                              </Box>
                              <Typography variant='subtitle2'>
                                {t('Individual Questionnaire')}
                              </Typography>
                              <Box py={4}>
                                {showIndividualQuestionnaire(values)}
                              </Box>
                              <BoxWithBorderBottom />
                            </>
                          )}
                          <Consent />
                          <Field
                            name='consent'
                            label={t('Received Consent*')}
                            color='primary'
                            fullWidth
                            container={false}
                            component={FormikCheckboxField}
                          />
                        </BoxWithBorders>
                      )}
                      {activeStep === steps.length - 1 && (
                        <BoxPadding>
                          <OverviewContainer>
                            <Grid container spacing={6}></Grid>
                          </OverviewContainer>
                          <BoxWithBorderBottom />
                          <BoxPadding />
                          <Grid container spacing={3}>
                            {values.subCategory ===
                              GRIEVANCE_SUB_CATEGORIES.PARTNER_COMPLAINT && (
                              <Grid item xs={3}>
                                <Field
                                  name='partner'
                                  fullWidth
                                  variant='outlined'
                                  label={t('Partner*')}
                                  choices={userChoices.userPartnerChoices}
                                  component={FormikSelectField}
                                />
                              </Grid>
                            )}
                            <Grid item xs={12}>
                              <Field
                                name='description'
                                multiline
                                fullWidth
                                variant='outlined'
                                label={
                                  values.issueType ===
                                    GRIEVANCE_ISSUE_TYPES.DELETE_HOUSEHOLD ||
                                  values.issueType ===
                                    GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL
                                    ? t('Withdrawal Reason*')
                                    : t('Description*')
                                }
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
                            <Grid item xs={3}>
                              <Field
                                name='priority'
                                multiline
                                fullWidth
                                variant='outlined'
                                label={t('Priority')}
                                choices={mappedPriorities}
                                component={FormikSelectField}
                              />
                            </Grid>
                            <Grid item xs={3}>
                              <Field
                                name='urgency'
                                multiline
                                fullWidth
                                variant='outlined'
                                label={t('Urgency')}
                                choices={mappedUrgencies}
                                component={FormikSelectField}
                              />
                            </Grid>
                            {+values.issueType !==
                              +GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL && (
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
                            )}
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
