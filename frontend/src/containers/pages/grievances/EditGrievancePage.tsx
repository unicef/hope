import {
  Box,
  Button,
  FormHelperText,
  Grid,
  Typography,
} from '@material-ui/core';
import { Field, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { ContainerColumnWithBorder } from '../../../components/core/ContainerColumnWithBorder';
import { ContentLink } from '../../../components/core/ContentLink';
import { LabelizedField } from '../../../components/core/LabelizedField';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { Title } from '../../../components/core/Title';
import { DocumentationFieldArray } from '../../../components/grievances/Documentation/DocumentationFieldArray';
import { LookUpPaymentRecord } from '../../../components/grievances/LookUps/LookUpPaymentRecord/LookUpPaymentRecord';
import { LookUpRelatedTickets } from '../../../components/grievances/LookUps/LookUpRelatedTickets/LookUpRelatedTickets';
import { OtherRelatedTicketsCreate } from '../../../components/grievances/OtherRelatedTicketsCreate';
import {
  dataChangeComponentDict,
  EmptyComponent,
  prepareInitialValues,
  prepareVariables,
} from '../../../components/grievances/utils/editGrievanceUtils';
import { validate } from '../../../components/grievances/utils/validateGrievance';
import { validationSchema } from '../../../components/grievances/utils/validationSchema';
import {
  hasCreatorOrOwnerPermissions,
  hasPermissions,
  PERMISSIONS,
} from '../../../config/permissions';
import { useArrayToDict } from '../../../hooks/useArrayToDict';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { FormikAdminAreaAutocomplete } from '../../../shared/Formik/FormikAdminAreaAutocomplete';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
  GRIEVANCE_TICKET_STATES,
} from '../../../utils/constants';
import {
  isInvalid,
  isPermissionDeniedError,
  reduceChoices,
  thingForSpecificGrievanceType,
} from '../../../utils/utils';
import {
  GrievanceTicketDocument,
  useAllAddIndividualFieldsQuery,
  useAllEditHouseholdFieldsQuery,
  useAllProgramsQuery,
  useAllUsersQuery,
  useGrievancesChoiceDataQuery,
  useGrievanceTicketQuery,
  useGrievanceTicketStatusChangeMutation,
  useMeQuery,
  useUpdateGrievanceMutation,
} from '../../../__generated__/graphql';
import { grievancePermissions } from './GrievancesDetailsPage/grievancePermissions';

const BoxPadding = styled.div`
  padding: 15px 0;
`;
const NewTicket = styled.div`
  padding: 20px;
`;
const BoxWithBorders = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

const BoxWithBottomBorders = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

export const EditGrievancePage = (): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const { id } = useParams();

  const {
    data: ticketData,
    loading: ticketLoading,
    error,
  } = useGrievanceTicketQuery({
    variables: {
      id,
    },
    fetchPolicy: 'cache-and-network',
  });

  const ticket = ticketData.grievanceTicket;

  const {
    data: currentUserData,
    loading: currentUserDataLoading,
  } = useMeQuery();

  const { data: userData, loading: userDataLoading } = useAllUsersQuery({
    variables: { businessArea, first: 1000 },
  });

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();

  const categoryChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketCategoryChoices);

  const [mutate, { loading }] = useUpdateGrievanceMutation();
  const [mutateStatus] = useGrievanceTicketStatusChangeMutation();
  const {
    data: allAddIndividualFieldsData,
    loading: allAddIndividualFieldsDataLoading,
  } = useAllAddIndividualFieldsQuery();
  const {
    data: householdFieldsData,
    loading: householdFieldsLoading,
  } = useAllEditHouseholdFieldsQuery();
  const individualFieldsDict = useArrayToDict(
    allAddIndividualFieldsData?.allAddIndividualsFieldsAttributes,
    'name',
    '*',
  );
  const householdFieldsDict = useArrayToDict(
    householdFieldsData?.allEditHouseholdFieldsAttributes,
    'name',
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

  if (
    userDataLoading ||
    choicesLoading ||
    ticketLoading ||
    allAddIndividualFieldsDataLoading ||
    householdFieldsLoading ||
    currentUserDataLoading ||
    loadingPrograms
  )
    return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (
    !choicesData ||
    !userData ||
    !ticketData ||
    !currentUserData ||
    permissions === null ||
    !householdFieldsData ||
    !householdFieldsDict ||
    !individualFieldsDict
  )
    return null;

  const currentUserId = currentUserData.me.id;

  const isCreator = ticket.createdBy?.id === currentUserId;
  const isOwner = ticket.assignedTo?.id === currentUserId;

  const {
    canViewHouseholdDetails,
    canViewIndividualDetails,
  } = grievancePermissions(isCreator, isOwner, ticket, permissions);

  if (
    !hasCreatorOrOwnerPermissions(
      PERMISSIONS.GRIEVANCES_UPDATE,
      isCreator,
      PERMISSIONS.GRIEVANCES_UPDATE_AS_CREATOR,
      isOwner,
      PERMISSIONS.GRIEVANCES_UPDATE_AS_OWNER,
      permissions,
    )
  )
    return <PermissionDenied />;

  const changeState = (status): void => {
    mutateStatus({
      variables: {
        grievanceTicketId: ticket.id,
        status,
      },
    });
  };
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const initialValues: any = prepareInitialValues(ticket);
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Grievance and Feedback'),
      to: `/${businessArea}/grievance-and-feedback/${ticket.id}`,
    },
  ];

  const issueTypeDict = choicesData.grievanceTicketIssueTypeChoices.reduce(
    (prev, curr) => {
      // eslint-disable-next-line no-param-reassign
      prev[curr.category] = curr;
      return prev;
    },
    {},
  );
  const showIssueType = (values): boolean => {
    return (
      values.category === GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE ||
      values.category === GRIEVANCE_CATEGORIES.DATA_CHANGE ||
      values.category === GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT
    );
  };
  const dataChangeErrors = (errors, touched): React.ReactElement[] =>
    [
      'householdDataUpdateFields',
      'individualDataUpdateFields',
      'individualDataUpdateFieldsDocuments',
      'individualDataUpdateFieldsIdentities',
      'individualDataUpdateDocumentsToEdit',
      'individualDataUpdateIdentitiesToEdit',
      'individualDataUpdateFieldsPaymentChannels',
      'individualDataUpdatePaymentChannelsToEdit',
    ].map(
      (fieldname) =>
        isInvalid(fieldname, errors, touched) && (
          <FormHelperText error>{errors[fieldname]}</FormHelperText>
        ),
    );

  const canAddDocumentation = hasPermissions(
    PERMISSIONS.GRIEVANCE_DOCUMENTS_UPLOAD,
    permissions,
  );

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        try {
          const { variables } = prepareVariables(businessArea, values, ticket);
          await mutate({
            variables,
            refetchQueries: () => [
              {
                query: GrievanceTicketDocument,
                variables: { id: ticket.id },
              },
            ],
          });
          showMessage(t('Grievance Ticket edited.'), {
            pathname: `/${businessArea}/grievance-and-feedback/${ticket.id}`,
            historyMethod: 'push',
          });
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
        if (
          ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL ||
          ticket.status === GRIEVANCE_TICKET_STATES.ON_HOLD
        ) {
          changeState(GRIEVANCE_TICKET_STATES.IN_PROGRESS);
        }
      }}
      validate={(values) =>
        validate(
          values,
          allAddIndividualFieldsData,
          individualFieldsDict,
          householdFieldsDict,
        )
      }
      validationSchema={validationSchema}
    >
      {({ submitForm, values, setFieldValue, errors, touched }) => {
        const DataChangeComponent = thingForSpecificGrievanceType(
          values,
          dataChangeComponentDict,
          EmptyComponent,
        );
        return (
          <>
            <PageHeader
              title={`${t('Edit Ticket')} #${ticket.unicefId}`}
              breadCrumbs={breadCrumbsItems}
            >
              <Box display='flex' alignContent='center'>
                <Box mr={3}>
                  <Button
                    component={Link}
                    to={`/${businessArea}/grievance-and-feedback/${ticket.id}`}
                  >
                    {t('Cancel')}
                  </Button>
                </Box>
                <LoadingButton
                  loading={loading}
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                >
                  {t('Save')}
                </LoadingButton>
              </Box>
            </PageHeader>
            <Grid spacing={3}>
              <Grid item xs={12}>
                <NewTicket>
                  <ContainerColumnWithBorder>
                    <Grid container spacing={3}>
                      <Grid item xs={3}>
                        <LabelizedField label={t('Category')}>
                          {categoryChoices[ticket.category]}
                        </LabelizedField>
                      </Grid>
                      {showIssueType(values) ? (
                        <Grid item xs={6}>
                          <Field
                            name='issueType'
                            disabled
                            label={t('Issue Type*')}
                            variant='outlined'
                            choices={
                              issueTypeDict[values.category.toString()]
                                .subCategories
                            }
                            component={FormikSelectField}
                          />
                        </Grid>
                      ) : null}
                      <Grid container xs={12} item>
                        <Grid item xs={3}>
                          <LabelizedField label={t('Household ID')}>
                            <span>
                              {ticket.household?.id ? (
                                <ContentLink
                                  href={
                                    canViewHouseholdDetails
                                      ? `/${businessArea}/population/household/${ticket.household.id}`
                                      : undefined
                                  }
                                >
                                  {ticket.household.unicefId}
                                </ContentLink>
                              ) : (
                                '-'
                              )}
                            </span>
                          </LabelizedField>
                        </Grid>
                        <Grid item xs={3}>
                          <LabelizedField label={t('Individual ID')}>
                            <span>
                              {ticket.individual?.id ? (
                                <ContentLink
                                  href={
                                    canViewIndividualDetails
                                      ? `/${businessArea}/population/individuals/${ticket.individual.id}`
                                      : undefined
                                  }
                                >
                                  {ticket.individual.unicefId}
                                </ContentLink>
                              ) : (
                                '-'
                              )}
                            </span>
                          </LabelizedField>
                        </Grid>
                      </Grid>
                    </Grid>
                    <BoxPadding>
                      <Grid container spacing={3}>
                        <Grid item xs={12}>
                          <Field
                            name='description'
                            multiline
                            fullWidth
                            disabled={Boolean(ticket.description)}
                            variant='outlined'
                            label='Description*'
                            component={FormikTextField}
                          />
                        </Grid>
                        <Grid item xs={12}>
                          <Field
                            name='comments'
                            multiline
                            fullWidth
                            disabled={Boolean(ticket.comments)}
                            variant='outlined'
                            label='Comments'
                            component={FormikTextField}
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <Field
                            name='admin'
                            label={t('Administrative Level 2')}
                            disabled={Boolean(ticket.admin)}
                            variant='outlined'
                            component={FormikAdminAreaAutocomplete}
                          />
                        </Grid>
                        <Grid item xs={6}>
                          <Field
                            name='area'
                            fullWidth
                            disabled={Boolean(ticket.area)}
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
                            disabled={Boolean(ticket.language)}
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
                            choices={choicesData.grievanceTicketPriorityChoices}
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
                            choices={choicesData.grievanceTicketUrgencyChoices}
                            component={FormikSelectField}
                          />
                        </Grid>
                        {ticket.issueType?.toString() !==
                          GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL.toString() && (
                          <Grid item xs={6}>
                            <Field
                              name='programme'
                              fullWidth
                              disabled={Boolean(ticket.programme)}
                              variant='outlined'
                              label={t('Programme Title')}
                              choices={mappedPrograms}
                              allProgramsEdges={allProgramsEdges}
                              component={FormikSelectField}
                            />
                          </Grid>
                        )}
                      </Grid>
                      {canAddDocumentation && (
                        <Box mt={3}>
                          <Title>
                            <Typography variant='h6'>
                              {t('Documentation')}
                            </Typography>
                          </Title>
                          <DocumentationFieldArray
                            values={values}
                            setFieldValue={setFieldValue}
                            errors={errors}
                          />
                        </Box>
                      )}
                    </BoxPadding>
                    <BoxPadding>
                      <BoxWithBorders>
                        <Grid item xs={6}>
                          <Box py={3}>
                            <LookUpRelatedTickets
                              values={values}
                              onValueChange={setFieldValue}
                            />
                          </Box>
                        </Grid>
                      </BoxWithBorders>
                      {(ticket.issueType?.toString() ===
                        GRIEVANCE_ISSUE_TYPES.PAYMENT_COMPLAINT ||
                        ticket.issueType?.toString() ===
                          GRIEVANCE_ISSUE_TYPES.FSP_COMPLAINT) && (
                        <BoxWithBottomBorders>
                          <Grid item xs={6}>
                            <Box py={3}>
                              <LookUpPaymentRecord
                                values={values}
                                disabled={Boolean(ticket.paymentRecord)}
                                onValueChange={setFieldValue}
                              />
                            </Box>
                          </Grid>
                        </BoxWithBottomBorders>
                      )}
                    </BoxPadding>
                    {hasCreatorOrOwnerPermissions(
                      PERMISSIONS.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE,
                      isCreator,
                      PERMISSIONS.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR,
                      isOwner,
                      PERMISSIONS.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER,
                      permissions,
                    ) && (
                      <BoxPadding>
                        <DataChangeComponent
                          values={values}
                          setFieldValue={setFieldValue}
                        />
                        {dataChangeErrors(errors, touched)}
                      </BoxPadding>
                    )}
                  </ContainerColumnWithBorder>
                </NewTicket>
              </Grid>
              <Grid item xs={6}>
                <NewTicket>
                  {values.category && values.selectedHousehold?.id ? (
                    <OtherRelatedTicketsCreate values={values} />
                  ) : null}
                </NewTicket>
              </Grid>
            </Grid>
          </>
        );
      }}
    </Formik>
  );
};
