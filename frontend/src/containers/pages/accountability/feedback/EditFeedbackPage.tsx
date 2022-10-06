import { Box, Button, Divider, Grid } from '@material-ui/core';
import { Field, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import * as Yup from 'yup';
import { BlackLink } from '../../../../components/core/BlackLink';
import { BreadCrumbsItem } from '../../../../components/core/BreadCrumbs';
import { ContainerColumnWithBorder } from '../../../../components/core/ContainerColumnWithBorder';
import { LabelizedField } from '../../../../components/core/LabelizedField';
import { LoadingButton } from '../../../../components/core/LoadingButton';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { PageHeader } from '../../../../components/core/PageHeader';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import {
  hasPermissionInModule,
  hasPermissions,
  PERMISSIONS,
} from '../../../../config/permissions';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { usePermissions } from '../../../../hooks/usePermissions';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { FormikAdminAreaAutocomplete } from '../../../../shared/Formik/FormikAdminAreaAutocomplete';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';
import {
  UpdateFeedbackInput,
  useAllProgramsQuery,
  useAllUsersQuery,
  useFeedbackIssueTypeChoicesQuery,
  useFeedbackQuery,
  useUpdateFeedbackTicketMutation,
} from '../../../../__generated__/graphql';

export const validationSchema = Yup.object().shape({
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
  comments: Yup.string().nullable(),
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

  const { feedback } = feedbackData;

  const initialValues = {
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

  const canViewHouseholdDetails = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
    permissions,
  );

  const canViewIndividualDetails = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_DETAILS,
    permissions,
  );

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
            >
              <Box display='flex' alignContent='center'>
                <Box mr={3}>
                  <Button
                    component={Link}
                    to={`/${businessArea}/accountability/feedback/${feedback.id}`}
                  >
                    {t('Cancel')}
                  </Button>
                </Box>
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
            </PageHeader>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Box p={3}>
                  <ContainerColumnWithBorder>
                    <Box p={3}>
                      <Box mb={3}>
                        <Grid container item xs={6} spacing={6}>
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
                        <Grid container xs={6} spacing={6}>
                          <Grid item xs={6}>
                            <LabelizedField label={t('Household ID')}>
                              {feedback.householdLookup?.id ? (
                                <BlackLink
                                  to={
                                    canViewHouseholdDetails
                                      ? `/${businessArea}/population/household/${feedback.householdLookup.id}`
                                      : undefined
                                  }
                                >
                                  {feedback.householdLookup.unicefId}
                                </BlackLink>
                              ) : (
                                '-'
                              )}
                            </LabelizedField>
                          </Grid>
                          <Grid item xs={6}>
                            <LabelizedField label={t('Individual ID')}>
                              {feedback.individualLookup?.id ? (
                                <BlackLink
                                  to={
                                    canViewIndividualDetails
                                      ? `/${businessArea}/population/individuals/${feedback.individualLookup.id}`
                                      : undefined
                                  }
                                >
                                  {feedback.individualLookup.unicefId}
                                </BlackLink>
                              ) : (
                                '-'
                              )}
                            </LabelizedField>
                          </Grid>
                        </Grid>
                        <Box mt={6} mb={6}>
                          <Divider />
                        </Box>
                      </Box>
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
                    </Box>
                  </ContainerColumnWithBorder>
                </Box>
              </Grid>
            </Grid>
          </>
        );
      }}
    </Formik>
  );
};
