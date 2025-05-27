import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { LabelizedField } from '@components/core/LabelizedField';
import { LoadingButton } from '@components/core/LoadingButton';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { OverviewContainer } from '@components/core/OverviewContainer';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { Consent } from '@components/grievances/Consent';
import HouseholdQuestionnaire from '@components/grievances/HouseholdQuestionnaire/HouseholdQuestionnaire';
import IndividualQuestionnaire from '@components/grievances/IndividualQuestionnnaire/IndividualQuestionnaire';
import { LookUpHouseholdIndividualSelection } from '@components/grievances/LookUps/LookUpHouseholdIndividual/LookUpHouseholdIndividualSelection';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  FormHelperText,
  Grid2 as Grid,
  Step,
  StepLabel,
  Stepper,
  Typography,
} from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { FormikAdminAreaAutocomplete } from '@shared/Formik/FormikAdminAreaAutocomplete';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useMutation, useQuery } from '@tanstack/react-query';
import { FeedbackSteps } from '@utils/constants';
import { Field, Formik } from 'formik';
import { ReactElement, ReactNode, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import * as Yup from 'yup';
import {
  PERMISSIONS,
  hasPermissionInModule,
  hasPermissions,
} from '../../../../config/permissions';
import { PaginatedProgramListList } from '@restgenerated/models/PaginatedProgramListList';
import { createApiParams } from '@utils/apiUtils';
import { decodeIdString } from '@utils/utils';

// Constants for feedback issue types
const FEEDBACK_ISSUE_TYPE = {
  POSITIVE_FEEDBACK: 'POSITIVE_FEEDBACK',
  NEGATIVE_FEEDBACK: 'NEGATIVE_FEEDBACK',
};

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
    category: Yup.string().required('Category is required'),
    issueType: Yup.string().required('Issue Type is required'),
    admin: Yup.string().nullable(),
    description: Yup.string().nullable(),
    consent: Yup.bool().nullable(),
    area: Yup.string().nullable(),
    language: Yup.string().nullable(),
    program: Yup.string().nullable(),
  };
  if (currentStep === FeedbackSteps.Description) {
    datum.description = Yup.string().required('Description is required');
    datum.language = Yup.string().required('Languages Spoken is required');
  }
  if (currentStep >= FeedbackSteps.Verification) {
    datum.consent = Yup.bool().oneOf([true], 'Consent is required');
  }
  return Yup.object().shape(datum);
};

// export function validateUsingSteps(
//   values,
//   activeStep,
//   setValidateData,
// ): { [key: string]: string | { [key: string]: string } } {
//   const errors: { [key: string]: string | { [key: string]: string } } = {};
// const verficationStepFields = [
//   'size',
//   'maleChildrenCount',
//   'femaleChildrenCount',
//   'childrenDisabledCount',
//   'headOfHousehold',
//   'countryOrigin',
//   'address',
//   'village',
//   'admin1',
//   'admin2',
//   'admin3',
//   'unhcrId',
//   'months_displaced_h_f',
//   'fullName',
//   'birthDate',
//   'phoneNo',
//   'relationship',
// ];

// if (
//   activeStep === FeedbackSteps.Verification &&
//   (values.selectedHousehold ||
//     (values.selectedIndividual && !values.verificationRequired))
// ) {
// const MIN_SELECTED_ITEMS = 5;
// const selectedItems = verficationStepFields.filter((item) => values[item]);

// TODO: enable this when questionnaire verification is required

// if (selectedItems.length < MIN_SELECTED_ITEMS) {
//   setValidateData(true);
//   errors.verificationRequired = 'Select correctly minimum 5 questions';
// }
// }
//   return errors;
// }

function CreateFeedbackPage(): ReactElement {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { baseUrl, businessArea, isAllPrograms, programId } = useBaseUrl();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const steps = [
    'Category Selection',
    `${beneficiaryGroup?.groupLabel}/${beneficiaryGroup?.memberLabel} Look up`,
    'Identity Verification',
    'Description',
  ];

  const [activeStep, setActiveStep] = useState(FeedbackSteps.Selection);

  const initialValues = {
    category: 'Feedback',
    issueType: null,
    selectedHousehold: null,
    selectedIndividual: null,
    description: '',
    comments: null,
    admin2: null,
    area: null,
    language: null,
    consent: false,
    program: isAllPrograms ? '' : programId,
    verificationRequired: false,
  };

  const { data: choicesData, isLoading: choicesLoading } = useQuery({
    queryKey: ['choicesFeedbackIssueTypeList', businessArea],
    queryFn: () => RestService.restChoicesFeedbackIssueTypeList(),
  });

  const { data: programsData, isLoading: programsDataLoading } =
    useQuery<PaginatedProgramListList>({
      queryKey: ['businessAreasProgramsList', { first: 100 }, businessArea],
      queryFn: () =>
        RestService.restBusinessAreasProgramsList(
          createApiParams(
            { businessAreaSlug: businessArea, first: 100 },
            {
              withPagination: false,
            },
          ),
        ),
    });

  const { mutateAsync: mutate, isPending: loading } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      requestBody,
    }: {
      businessAreaSlug: string;
      requestBody;
    }) =>
      RestService.restBusinessAreasFeedbacksCreate({
        businessAreaSlug,
        requestBody,
      }),
  });

  if (choicesLoading || programsDataLoading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.GRIEVANCES_FEEDBACK_VIEW_CREATE, permissions))
    return <PermissionDenied />;

  if (!choicesData || !programsData) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Feedback'),
      to: `/${baseUrl}/grievance/feedback/`,
    },
  ];

  const handleNext = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const prepareVariables = (values) => ({
    area: values.area,
    comments: values.comments,
    consent: values.consent,
    description: values.description,
    householdLookup: values.selectedHousehold?.id,
    individualLookup: values.selectedIndividual?.id,
    issueType: values.issueType,
    admin2: decodeIdString(values.admin2),
    language: values.language,
    program: values.program,
  });

  const mappedProgramChoices = programsData?.results?.map((element) => ({
    name: element.name,
    value: element.id,
  }));

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        if (activeStep === steps.length - 1) {
          try {
            const response = await mutate({
              businessAreaSlug: businessArea,
              requestBody: prepareVariables(values),
            });
            showMessage(t('Feedback created'));
            navigate(`/${baseUrl}/grievance/feedback/${response.id}`);
          } catch (e) {
            showMessage(e.message || 'Error creating feedback');
          }
        } else {
          handleNext();
        }
      }}
      validateOnChange={true}
      validateOnBlur={true}
      validationSchema={validationSchemaWithSteps(activeStep)}
      // validate={(values) =>
      //   validateUsingSteps(values, activeStep, setValidateData)
      // }
    >
      {({ submitForm, values, setFieldValue, errors, touched }) => {
        const isAnonymousTicket =
          !values.selectedHousehold?.id && !values.selectedIndividual?.id;

        // Set program value based on selected household or individual
        if (
          values.selectedHousehold?.program?.id &&
          values.program !== values.selectedHousehold.program.id
        ) {
          setFieldValue('program', values.selectedHousehold.program.id);
        } else if (
          values.selectedIndividual?.program?.id &&
          values.program !== values.selectedIndividual.program.id
        ) {
          setFieldValue('program', values.selectedIndividual.program.id);
        }
        return (
          <>
            <PageHeader
              title="New Feedback"
              breadCrumbs={
                hasPermissionInModule(
                  'GRIEVANCES_FEEDBACK_VIEW_LIST',
                  permissions,
                )
                  ? breadCrumbsItems
                  : null
              }
            />
            <Grid container spacing={3}>
              <Grid size={{ xs: 12 }}>
                <NewTicket>
                  <InnerBoxPadding>
                    <ContainerColumnWithBorder>
                      <NoRootPadding>
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
                      </NoRootPadding>
                      {activeStep === FeedbackSteps.Selection && (
                        <Grid container spacing={3}>
                          <Grid size={{ xs: 6 }}>
                            <LabelizedField label={t('Category')}>
                              {t('Feedback')}
                            </LabelizedField>
                          </Grid>
                          <Grid size={{ xs: 6 }}>
                            <Field
                              name="issueType"
                              label="Issue Type"
                              variant="outlined"
                              required
                              choices={choicesData}
                              component={FormikSelectField}
                              data-cy="input-issue-type"
                            />
                          </Grid>
                        </Grid>
                      )}
                      {activeStep === FeedbackSteps.Lookup && (
                        <BoxWithBorders>
                          <Box display="flex" flexDirection="column">
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
                              {/* //TODO: Optional for now */}
                              {/* <Typography variant='subtitle1'>
                                {t(
                                  'Select correctly answered questions (minimum 5)',
                                )}
                              </Typography> */}
                              <Box py={4}>
                                <Typography variant="subtitle2">
                                  {t(
                                    `${beneficiaryGroup?.groupLabel} Questionnaire`,
                                  )}
                                </Typography>
                                <Box py={4}>
                                  <HouseholdQuestionnaire values={values} />
                                </Box>
                              </Box>
                              <Typography variant="subtitle2">
                                {t(
                                  `${beneficiaryGroup?.memberLabel} Questionnaire`,
                                )}
                              </Typography>
                              <Box py={4}>
                                <IndividualQuestionnaire values={values} />
                              </Box>
                              <BoxWithBorderBottom />
                            </>
                          )}
                          <Consent />
                          <Field
                            name="consent"
                            label={t('Received Consent')}
                            color="primary"
                            fullWidth
                            required
                            container={false}
                            component={FormikCheckboxField}
                            data-cy="input-consent"
                          />
                        </BoxWithBorders>
                      )}
                      {activeStep === steps.length - 1 && (
                        <BoxPadding>
                          <OverviewContainer>
                            <Box p={6}>
                              <Grid container spacing={6}>
                                <Grid size={{ xs: 6 }}>
                                  <LabelizedField label={t('Category')}>
                                    {t('Feedback')}
                                  </LabelizedField>
                                </Grid>
                                <Grid size={{ xs: 6 }}>
                                  <LabelizedField label={t('Issue Type')}>
                                    {values.issueType ===
                                    FEEDBACK_ISSUE_TYPE.POSITIVE_FEEDBACK
                                      ? 'Positive Feedback'
                                      : 'Negative Feedback'}
                                  </LabelizedField>
                                </Grid>
                                <Grid size={{ xs: 6 }}>
                                  <LabelizedField
                                    label={t(`${beneficiaryGroup?.groupLabel}`)}
                                  >
                                    {values.selectedHousehold?.unicefId}
                                  </LabelizedField>
                                </Grid>
                                <Grid size={{ xs: 6 }}>
                                  <LabelizedField
                                    label={t(
                                      `${beneficiaryGroup?.memberLabel}`,
                                    )}
                                  >
                                    {values.selectedIndividual?.unicefId}
                                  </LabelizedField>
                                </Grid>
                              </Grid>
                            </Box>
                          </OverviewContainer>
                          <BoxWithBorderBottom />
                          <BoxPadding />
                          <Grid container spacing={3}>
                            <Grid size={{ xs: 12 }}>
                              <Field
                                name="description"
                                multiline
                                fullWidth
                                variant="outlined"
                                label={t('Description')}
                                required
                                component={FormikTextField}
                                data-cy="input-description"
                              />
                            </Grid>
                            <Grid size={{ xs: 12 }}>
                              <Field
                                name="comments"
                                multiline
                                fullWidth
                                variant="outlined"
                                label={t('Comments')}
                                component={FormikTextField}
                                data-cy="input-comments"
                              />
                            </Grid>
                            <Grid size={{ xs: 6 }}>
                              <Field
                                name="admin2"
                                variant="outlined"
                                component={FormikAdminAreaAutocomplete}
                                dataCy="input-admin2"
                                disabled={Boolean(
                                  values.selectedHousehold?.admin2,
                                )}
                              />
                            </Grid>
                            <Grid size={{ xs: 6 }}>
                              <Field
                                name="area"
                                fullWidth
                                variant="outlined"
                                label={t('Area / Village / Pay point')}
                                component={FormikTextField}
                                data-cy="input-area"
                              />
                            </Grid>
                            <Grid size={{ xs: 6 }}>
                              <Field
                                name="language"
                                multiline
                                fullWidth
                                variant="outlined"
                                label={t('Languages Spoken')}
                                component={FormikTextField}
                                data-cy="input-languages"
                                required
                              />
                            </Grid>
                            <Grid size={{ xs: 3 }}>
                              <Field
                                name="program"
                                label={t('Programme Name')}
                                fullWidth
                                variant="outlined"
                                choices={mappedProgramChoices}
                                component={FormikSelectField}
                                disabled={!isAllPrograms || !isAnonymousTicket}
                              />
                            </Grid>
                          </Grid>
                        </BoxPadding>
                      )}
                      {errors.verificationRequired ? (
                        <FormHelperText error>
                          {errors.verificationRequired}
                        </FormHelperText>
                      ) : null}
                      <Box pt={3} display="flex" flexDirection="row">
                        <Box mr={3}>
                          <Button
                            component={Link}
                            to={`/${baseUrl}/grievance/feedback`}
                            data-cy="button-cancel"
                          >
                            {t('Cancel')}
                          </Button>
                        </Box>
                        <Box display="flex" ml="auto">
                          <Button
                            disabled={activeStep === 0}
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
                            disabled={
                              activeStep === steps.length - 1
                                ? // On final step, check only fields required for this step
                                  !values.description ||
                                  !values.language ||
                                  Object.keys(errors).includes('description') ||
                                  Object.keys(errors).includes('language')
                                : // On earlier steps, check if there are any errors for fields on the current step
                                  Object.keys(errors).length > 0
                            }
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
}

export default withErrorBoundary(CreateFeedbackPage, 'CreateFeedbackPage');
