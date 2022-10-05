import {
  Box,
  Button,
  FormHelperText,
  Grid,
  Step,
  StepLabel,
  Stepper,
  Typography,
} from '@material-ui/core';
import { Field, Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
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
import {
  hasPermissionInModule,
  hasPermissions,
  PERMISSIONS,
} from '../../../../config/permissions';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { usePermissions } from '../../../../hooks/usePermissions';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { FormikAdminAreaAutocomplete } from '../../../../shared/Formik/FormikAdminAreaAutocomplete';
import { FormikCheckboxField } from '../../../../shared/Formik/FormikCheckboxField';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';
import { FeedbackSteps } from '../../../../utils/constants';
import {
  UpdateFeedbackInput,
  useAllProgramsQuery,
  useAllUsersQuery,
  useFeedbackIssueTypeChoicesQuery,
  useFeedbackQuery,
  useUpdateFeedbackTicketMutation,
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

export const validationSchema = Yup.object().shape({
  category: Yup.string()
    .required('Category is required')
    .nullable(),
  issueType: Yup.string()
    .required('Issue Type is required')
    .nullable(),
  admin: Yup.string().nullable(),
  description: Yup.string()
    .nullable()
    .required('Description is required'),
  consent: Yup.bool(),
  area: Yup.string().nullable(),
  language: Yup.string().nullable(),
  selectedPaymentRecords: Yup.array()
    .of(Yup.string())
    .nullable(),
  selectedRelatedTickets: Yup.array()
    .of(Yup.string())
    .nullable(),
});

export const EditFeedbackPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const { data: feedbackData, loading: feedbackDataLoading } = useFeedbackQuery(
    {
      variables: { id },
      fetchPolicy: 'network-only',
    },
  );

  const [activeStep, setActiveStep] = useState(FeedbackSteps.Selection);
  const [validateData, setValidateData] = useState(false);

  const { data: userData, loading: userDataLoading } = useAllUsersQuery({
    variables: { businessArea, first: 1000 },
  });

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useFeedbackIssueTypeChoicesQuery();

  const [mutate, { loading }] = useUpdateFeedbackTicketMutation();

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

  if (
    userDataLoading ||
    choicesLoading ||
    loadingPrograms ||
    feedbackDataLoading
  )
    return <LoadingComponent />;
  if (permissions === null) return null;
  if (
    !hasPermissions(
      PERMISSIONS.ACCOUNTABILITY_FEEDBACK_VIEW_CREATE,
      permissions,
    )
  )
    return <PermissionDenied />;

  if (!choicesData || !userData || !feedbackData) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Feedback'),
      to: `/${businessArea}/accountability/feedback/${id}`,
    },
  ];

  const handleNext = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const { feedback } = feedbackData;

  const initialValues = {
    category: 'Feedback',
    issueType: feedback.issueType,
    selectedHousehold: feedback.householdLookup || null,
    selectedIndividual: feedback.individualLookup || null,
    description: feedback.description || null,
    comments: feedback.comments || null,
    admin2: feedback.admin2?.name || null,
    area: feedback.area || null,
    language: feedback.language || null,
    consent: false,
    program: feedback.program?.id || null,
    verificationRequired: false,
  };

  const prepareVariables = (values): UpdateFeedbackInput => ({
    feedbackId: id,
    issueType: values.issueType,
    householdLookup: values.selectedHousehold?.id,
    individualLookup: values.selectedIndividual?.id,
    description: values.description,
    comments: values.comments,
    admin2: values.admin2?.node.id,
    area: values.area,
    language: values.language,
    consent: values.consent,
    program: values.program,
  });

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        try {
          const response = await mutate({
            variables: { input: prepareVariables(values) },
          });
          showMessage(t('Feedback updated'), {
            pathname: `/${businessArea}/accountability/feedback/${response.data.updateFeedback.feedback.id}`,
            historyMethod: 'push',
          });
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
      }}
      validationSchema={validationSchema}
    >
      {({ submitForm }) => {
        return (
          <>
            <PageHeader
              title={`Edit Feedback #${feedback.unicefId}`}
              breadCrumbs={
                hasPermissionInModule(
                  'ACCOUNTABILITY_FEEDBACK_VIEW_LIST',
                  permissions,
                )
                  ? breadCrumbsItems
                  : null
              }
            />
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <NewTicket>
                  <InnerBoxPadding>
                    <ContainerColumnWithBorder>
                      <BoxPadding>
                        <Grid container spacing={6}>
                          <Grid item xs={6}>
                            <LabelizedField label={t('Category')}>
                              {t('Feedback')}
                            </LabelizedField>
                          </Grid>
                          <Grid item xs={6}>
                            <LabelizedField label={t('Issue Type')}>
                              {feedback.issueType === 'POSITIVE_FEEDBACK'
                                ? 'Positive Feedback'
                                : 'Negative Feedback'}
                            </LabelizedField>
                          </Grid>
                        </Grid>
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
                              name='admin2'
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
                              name='program'
                              fullWidth
                              variant='outlined'
                              label={t('Programme Title')}
                              choices={mappedPrograms}
                              component={FormikSelectField}
                            />
                          </Grid>
                        </Grid>
                      </BoxPadding>
                      <Box display='flex' justifyContent='space-between'>
                        <Button
                          component={Link}
                          to={`/${businessArea}/accountability/feedback/${feedback.id}`}
                        >
                          {t('Cancel')}
                        </Button>
                        <LoadingButton
                          loading={loading}
                          color='primary'
                          variant='contained'
                          onClick={submitForm}
                          data-cy='button-submit'
                        >
                          {t('Save')}
                        </LoadingButton>
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
