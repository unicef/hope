import type { BreadCrumbsItem } from '@components/core/BreadCrumbs';
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
import { Button, FormHelperText, Typography } from '@mui/material';
import { Box } from '@mui/system';
import { RestService } from '@restgenerated/index';
import type { PaginatedProgramListList } from '@restgenerated/models/PaginatedProgramListList';
import { FormikAdminAreaAutocomplete } from '@shared/Formik/FormikAdminAreaAutocomplete';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { createApiParams } from '@utils/apiUtils';
import { FeedbackSteps } from '@utils/constants';
import { showApiErrorMessages } from '@utils/utils';
import { Field, Formik } from 'formik';
import type { ReactElement, ReactNode } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import * as Yup from 'yup';
import { Admin2SyncEffect } from './Admin2SyncEffect';
import { ProgramIdSyncEffect } from './ProgramIdSyncEffect';
import { CreateGrievanceStepper } from '@components/grievances/CreateGrievance/CreateGrievanceStepper/CreateGrievanceStepper';
import {
  ResponsiveGrid,
  ResponsiveGridContainer,
  responsiveValue,
} from 'src/responsive';

const FEEDBACK_ISSUE_TYPE = {
  POSITIVE_FEEDBACK: 'POSITIVE_FEEDBACK',
  NEGATIVE_FEEDBACK: 'NEGATIVE_FEEDBACK',
};

const BoxPadding = styled.div`
  padding: 15px 0;
`;
function InnerBoxPadding({ children }: { children: ReactNode }): ReactElement {
  return (
    <Box
      sx={{
        '& .MuiPaper-root': { padding: responsiveValue('16px', '32px 20px') },
      }}
    >
      {children}
    </Box>
  );
}
function NewTicket({ children }: { children: ReactNode }): ReactElement {
  return <Box sx={{ padding: responsiveValue('8px', '20px') }}>{children}</Box>;
}
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
    programId: Yup.string().nullable(),
  };
  if (currentStep === FeedbackSteps.Description) {
    datum.description = Yup.string().required('Description is required');
  }
  if (currentStep >= FeedbackSteps.Verification) {
    datum.consent = Yup.bool().oneOf([true], 'Consent is required');
  }
  return Yup.object().shape(datum);
};

function CreateFeedbackPage(): ReactElement {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { baseUrl, businessArea, isAllPrograms } = useBaseUrl();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const { selectedProgram, isSocialDctType } = useProgramContext();
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
    verificationRequired: false,
    programId: isAllPrograms ? null : selectedProgram?.id,
  };

  const { data: choicesData, isLoading: choicesLoading } = useQuery({
    queryKey: restQueryKey(RestService.restChoicesFeedbackIssueTypeList),
    queryFn: () => RestService.restChoicesFeedbackIssueTypeList(),
  });

  const programsParams = createApiParams(
    { businessAreaSlug: businessArea, limit: 100 },
    {
      withPagination: false,
    },
  );

  const { data: programsData, isLoading: programsDataLoading } =
    useQuery<PaginatedProgramListList>({
      queryKey: restQueryKey(
        RestService.restBusinessAreasProgramsList,
        programsParams,
      ),
      queryFn: () => RestService.restBusinessAreasProgramsList(programsParams),
    });

  const queryClient = useQueryClient();
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
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsFeedbacksList,
        ),
      });
      queryClient.invalidateQueries({
        queryKey: restQueryKey(RestService.restBusinessAreasFeedbacksList),
      });
    },
  });

  if (choicesLoading || programsDataLoading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.GRIEVANCES_FEEDBACK_VIEW_CREATE, permissions))
    return (
      <PermissionDenied
        permission={PERMISSIONS.GRIEVANCES_FEEDBACK_VIEW_CREATE}
      />
    );

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
    admin2:
      typeof values.admin2 === 'object' && values.admin2 !== null
        ? values.admin2.id
        : values.admin2,
    language: values.language || '',
    programId: values.programId || null,
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
            showApiErrorMessages(e, showMessage, 'Error creating feedback');
          }
        } else {
          handleNext();
        }
      }}
      validateOnChange={true}
      validateOnBlur={true}
      validationSchema={validationSchemaWithSteps(activeStep)}
    >
      {({ submitForm, values, setFieldValue, errors, touched }) => {
        // Sync admin2 with selectedHousehold.admin2
        <Admin2SyncEffect
          selectedHousehold={values.selectedHousehold}
          admin2={values.admin2}
          setFieldValue={setFieldValue}
        />;
        const isAnonymousTicket =
          !values.selectedHousehold?.id && !values.selectedIndividual?.id;

        return (
          <>
            <ProgramIdSyncEffect />
            <Admin2SyncEffect
              selectedHousehold={values.selectedHousehold}
              admin2={values.admin2}
              setFieldValue={setFieldValue}
            />
            <PageHeader
              title="New Feedback"
              breadCrumbs={
                hasPermissions(
                  PERMISSIONS.GRIEVANCES_FEEDBACK_VIEW_LIST,
                  permissions,
                )
                  ? breadCrumbsItems
                  : null
              }
            />
            <ResponsiveGridContainer spacing={3}>
              <ResponsiveGrid size="full">
                <NewTicket>
                  <InnerBoxPadding>
                    <ContainerColumnWithBorder>
                      <CreateGrievanceStepper
                        activeStep={activeStep}
                        steps={steps}
                      />
                      {activeStep === FeedbackSteps.Selection && (
                        <ResponsiveGridContainer spacing={3}>
                          <ResponsiveGrid size="half">
                            <LabelizedField label={t('Category')}>
                              {t('Feedback')}
                            </LabelizedField>
                          </ResponsiveGrid>
                          <ResponsiveGrid size="half">
                            <Field
                              name="issueType"
                              label="Issue Type"
                              variant="outlined"
                              required
                              choices={choicesData}
                              component={FormikSelectField}
                              data-cy="input-issue-type"
                            />
                          </ResponsiveGrid>
                        </ResponsiveGridContainer>
                      )}
                      {activeStep === FeedbackSteps.Lookup && (
                        <BoxWithBorders>
                          <Box
                            sx={{
                              display: 'flex',
                              flexDirection: 'column',
                            }}
                          >
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
                              {!isSocialDctType && (
                                <Box
                                  sx={{
                                    py: 4,
                                  }}
                                >
                                  <Typography variant="subtitle2">
                                    {t(
                                      `${beneficiaryGroup?.groupLabel} Questionnaire`,
                                    )}
                                  </Typography>
                                  <Box
                                    sx={{
                                      py: 4,
                                    }}
                                  >
                                    <HouseholdQuestionnaire
                                      values={values}
                                      programCode={
                                        values.selectedHousehold?.programCode ||
                                        values.selectedHousehold?.program
                                          ?.code ||
                                        values.selectedIndividual?.program
                                          ?.code ||
                                        values.selectedIndividual?.programCode
                                      }
                                    />
                                  </Box>
                                </Box>
                              )}
                              <Typography variant="subtitle2">
                                {t(
                                  `${beneficiaryGroup?.memberLabel} Questionnaire`,
                                )}
                              </Typography>
                              <Box
                                sx={{
                                  py: 4,
                                }}
                              >
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
                            <Box
                              sx={{
                                p: 6,
                              }}
                            >
                              <ResponsiveGridContainer spacing={6}>
                                <ResponsiveGrid size="half">
                                  <LabelizedField label={t('Category')}>
                                    {t('Feedback')}
                                  </LabelizedField>
                                </ResponsiveGrid>
                                <ResponsiveGrid size="half">
                                  <LabelizedField label={t('Issue Type')}>
                                    {values.issueType ===
                                    FEEDBACK_ISSUE_TYPE.POSITIVE_FEEDBACK
                                      ? 'Positive Feedback'
                                      : 'Negative Feedback'}
                                  </LabelizedField>
                                </ResponsiveGrid>
                                {!isSocialDctType && (
                                  <ResponsiveGrid size="half">
                                    <LabelizedField
                                      label={t(
                                        `${beneficiaryGroup?.groupLabel}`,
                                      )}
                                    >
                                      {values.selectedHousehold?.unicefId}
                                    </LabelizedField>
                                  </ResponsiveGrid>
                                )}
                                <ResponsiveGrid size="half">
                                  <LabelizedField
                                    label={t(
                                      `${beneficiaryGroup?.memberLabel}`,
                                    )}
                                  >
                                    {values.selectedIndividual?.unicefId}
                                  </LabelizedField>
                                </ResponsiveGrid>
                              </ResponsiveGridContainer>
                            </Box>
                          </OverviewContainer>
                          <BoxWithBorderBottom />
                          <BoxPadding />
                          <ResponsiveGridContainer spacing={3}>
                            <ResponsiveGrid size="full">
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
                            </ResponsiveGrid>
                            <ResponsiveGrid size="full">
                              <Field
                                name="comments"
                                multiline
                                fullWidth
                                variant="outlined"
                                label={t('Comments')}
                                component={FormikTextField}
                                data-cy="input-comments"
                              />
                            </ResponsiveGrid>
                            <ResponsiveGrid size="half">
                              <Field
                                name="admin2"
                                variant="outlined"
                                component={FormikAdminAreaAutocomplete}
                                dataCy="input-admin2"
                              />
                              {touched.admin2 &&
                                typeof errors.admin2 === 'string' && (
                                  <FormHelperText error>
                                    {errors.admin2}
                                  </FormHelperText>
                                )}
                            </ResponsiveGrid>
                            <ResponsiveGrid size="half">
                              <Field
                                name="area"
                                fullWidth
                                variant="outlined"
                                label={t('Area / Village / Pay point')}
                                component={FormikTextField}
                                data-cy="input-area"
                              />
                              {touched.area &&
                                typeof errors.area === 'string' && (
                                  <FormHelperText error>
                                    {errors.area}
                                  </FormHelperText>
                                )}
                            </ResponsiveGrid>
                            <ResponsiveGrid size="half">
                              <Field
                                name="language"
                                multiline
                                fullWidth
                                variant="outlined"
                                label={t('Languages Spoken')}
                                component={FormikTextField}
                                data-cy="input-languages"
                              />
                              {touched.language &&
                                typeof errors.language === 'string' && (
                                  <FormHelperText error>
                                    {errors.language}
                                  </FormHelperText>
                                )}
                            </ResponsiveGrid>
                            <ResponsiveGrid size="quarter">
                              <Field
                                name="programId"
                                label={t('Programme Name')}
                                fullWidth
                                variant="outlined"
                                choices={mappedProgramChoices}
                                component={FormikSelectField}
                                disabled={!isAllPrograms || !isAnonymousTicket}
                              />
                              {touched.programId &&
                                typeof errors.programId === 'string' && (
                                  <FormHelperText error>
                                    {errors.programId}
                                  </FormHelperText>
                                )}
                            </ResponsiveGrid>
                          </ResponsiveGridContainer>
                        </BoxPadding>
                      )}
                      {errors.verificationRequired ? (
                        <FormHelperText error>
                          {errors.verificationRequired}
                        </FormHelperText>
                      ) : null}
                      <Box
                        sx={{
                          pt: 3,
                          display: 'flex',
                          flexDirection: 'row',
                        }}
                      >
                        <Box
                          sx={{
                            mr: 3,
                          }}
                        >
                          <Button
                            component={Link}
                            to={`/${baseUrl}/grievance/feedback`}
                            data-cy="button-cancel"
                          >
                            {t('Cancel')}
                          </Button>
                        </Box>
                        <Box
                          sx={{
                            display: 'flex',
                            ml: 'auto',
                          }}
                        >
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
              </ResponsiveGrid>
            </ResponsiveGridContainer>
          </>
        );
      }}
    </Formik>
  );
}

export default withErrorBoundary(CreateFeedbackPage, 'CreateFeedbackPage');
