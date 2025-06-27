import { Box, Button, Divider, Grid2 as Grid } from '@mui/material';
import { Field, Formik } from 'formik';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useParams } from 'react-router-dom';
import * as Yup from 'yup';
import {
  UpdateFeedbackInput,
  useAllProgramsForChoicesQuery,
  useAllUsersQuery,
  useFeedbackIssueTypeChoicesQuery,
  useFeedbackQuery,
  useUpdateFeedbackTicketMutation,
} from '@generated/graphql';
import { BlackLink } from '@components/core/BlackLink';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { LabelizedField } from '@components/core/LabelizedField';
import { LoadingButton } from '@components/core/LoadingButton';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import {
  PERMISSIONS,
  hasPermissionInModule,
  hasPermissions,
} from '../../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { FormikAdminAreaAutocomplete } from '@shared/Formik/FormikAdminAreaAutocomplete';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

export const validationSchema = Yup.object().shape({
  issueType: Yup.string().required('Issue Type is required').nullable(),
  admin2: Yup.string().nullable(),
  description: Yup.string().nullable().required('Description is required'),
  consent: Yup.bool(),
  area: Yup.string().nullable(),
  language: Yup.string().nullable(),
  comments: Yup.string().nullable(),
});

const EditFeedbackPage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { id } = useParams();
  const { baseUrl, businessArea, isAllPrograms } = useBaseUrl();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const { data: feedbackData, loading: feedbackDataLoading } = useFeedbackQuery(
    {
      variables: { id },
      fetchPolicy: 'network-only',
    },
  );

  const { data: userData, loading: userDataLoading } = useAllUsersQuery({
    variables: { businessArea, first: 1000 },
  });

  const { data: choicesData, loading: choicesLoading } =
    useFeedbackIssueTypeChoicesQuery();

  const { data: programsData, loading: programsDataLoading } =
    useAllProgramsForChoicesQuery({
      variables: {
        first: 100,
        businessArea,
      },
    });

  const [mutate, { loading }] = useUpdateFeedbackTicketMutation();

  if (
    userDataLoading ||
    choicesLoading ||
    feedbackDataLoading ||
    programsDataLoading
  )
    return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.GRIEVANCES_FEEDBACK_VIEW_CREATE, permissions))
    return <PermissionDenied />;

  if (!choicesData || !userData || !feedbackData || !programsData) return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Feedback'),
      to: `/${baseUrl}/grievance/feedback/${id}`,
    },
  ];

  const { feedback } = feedbackData;

  const initialValues = {
    issueType: feedback.issueType,
    selectedHousehold: feedback.householdLookup || null,
    selectedIndividual: feedback.individualLookup || null,
    description: feedback.description || null,
    comments: feedback.comments || null,
    admin2: feedback.admin2?.id || null,
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
    admin2: values.admin2,
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

  const mappedProgramChoices = programsData?.allPrograms?.edges?.map(
    (element) => ({ name: element.node.name, value: element.node.id }),
  );

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        try {
          const response = await mutate({
            variables: { input: prepareVariables(values) },
          });
          showMessage(t('Feedback updated'));
          navigate(
            `/${baseUrl}/grievance/feedback/${response.data.updateFeedback.feedback.id}`,
          );
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
      }}
      validationSchema={validationSchema}
    >
      {({ submitForm }) => (
        <>
          <PageHeader
            title={`Edit Feedback #${feedback.unicefId}`}
            breadCrumbs={
              hasPermissionInModule(
                'GRIEVANCES_FEEDBACK_VIEW_LIST',
                permissions,
              )
                ? breadCrumbsItems
                : null
            }
          >
            <Box display="flex" alignContent="center">
              <Box mr={3}>
                <Button
                  component={Link}
                  to={`/${baseUrl}/grievance/feedback/${feedback.id}`}
                >
                  {t('Cancel')}
                </Button>
              </Box>
              <LoadingButton
                loading={loading}
                color="primary"
                variant="contained"
                onClick={submitForm}
                data-cy="button-submit"
              >
                {t('Save')}
              </LoadingButton>
            </Box>
          </PageHeader>
          <Grid container spacing={3}>
            <Grid size={{ xs: 12 }}>
              <Box p={3}>
                <ContainerColumnWithBorder>
                  <Box p={3}>
                    <Box mb={3}>
                      <Grid container size={{ xs: 6 }} spacing={6}>
                        <Grid size={{ xs: 6 }}>
                          <LabelizedField label={t('Category')}>
                            {t('Feedback')}
                          </LabelizedField>
                        </Grid>
                        <Grid size={{ xs: 6 }}>
                          <LabelizedField label={t('Issue Type')}>
                            {feedback.issueType === 'POSITIVE_FEEDBACK'
                              ? 'Positive Feedback'
                              : 'Negative Feedback'}
                          </LabelizedField>
                        </Grid>
                      </Grid>
                      <Grid container size={{ xs: 6 }} spacing={6}>
                        <Grid size={{ xs: 6 }}>
                          <LabelizedField
                            label={t(`${beneficiaryGroup?.groupLabel} ID`)}
                          >
                            {' '}
                            {feedback.householdLookup?.id &&
                            canViewHouseholdDetails &&
                            !isAllPrograms ? (
                              <BlackLink
                                to={`/${baseUrl}/population/household/${feedback.householdLookup?.id}`}
                              >
                                {feedback.householdLookup?.unicefId}
                              </BlackLink>
                            ) : (
                              <div>
                                {feedback.householdLookup?.id
                                  ? feedback.householdLookup?.unicefId
                                  : '-'}
                              </div>
                            )}
                          </LabelizedField>
                        </Grid>
                        <Grid size={{ xs: 6 }}>
                          <LabelizedField
                            label={t(`${beneficiaryGroup?.memberLabel} ID`)}
                          >
                            {' '}
                            {feedback.individualLookup?.id &&
                            canViewIndividualDetails &&
                            !isAllPrograms ? (
                              <BlackLink
                                to={`/${baseUrl}/population/individuals/${feedback.individualLookup?.id}`}
                              >
                                {feedback.individualLookup?.unicefId}
                              </BlackLink>
                            ) : (
                              <div>
                                {feedback.individualLookup?.id
                                  ? feedback.individualLookup?.unicefId
                                  : '-'}
                              </div>
                            )}
                          </LabelizedField>
                        </Grid>
                      </Grid>
                      <Box mt={6} mb={6}>
                        <Divider />
                      </Box>
                    </Box>
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
                        />
                      </Grid>
                      <Grid size={{ xs: 6 }}>
                        <Field
                          name="admin2"
                          variant="outlined"
                          component={FormikAdminAreaAutocomplete}
                          disabled={Boolean(feedback.admin2?.id)}
                        />
                      </Grid>
                      <Grid size={{ xs: 6 }}>
                        <Field
                          name="area"
                          fullWidth
                          variant="outlined"
                          label={t('Area / Village / Pay point')}
                          component={FormikTextField}
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
                          disabled={
                            !isAllPrograms || Boolean(feedback.program?.id)
                          }
                        />
                      </Grid>
                    </Grid>
                  </Box>
                </ContainerColumnWithBorder>
              </Box>
            </Grid>
          </Grid>
        </>
      )}
    </Formik>
  );
};

export default withErrorBoundary(EditFeedbackPage, 'EditFeedbackPage');
