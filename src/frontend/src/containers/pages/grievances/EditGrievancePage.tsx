import {
  Box,
  Button,
  FormHelperText,
  Grid2 as Grid,
  Typography,
} from '@mui/material';
import { Field, Formik } from 'formik';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useParams } from 'react-router-dom';
import styled from 'styled-components';
import {
  GrievanceTicketDocument,
  useAllAddIndividualFieldsQuery,
  useAllEditHouseholdFieldsQuery,
  useAllEditPeopleFieldsQuery,
  useAllProgramsForChoicesQuery,
  useGrievanceTicketQuery,
  useGrievanceTicketStatusChangeMutation,
  useGrievancesChoiceDataQuery,
  useMeQuery,
  useUpdateGrievanceMutation,
} from '@generated/graphql';
import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { BlackLink } from '@components/core/BlackLink';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { DividerLine } from '@components/core/DividerLine';
import { LabelizedField } from '@components/core/LabelizedField';
import { LoadingButton } from '@components/core/LoadingButton';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { Title } from '@components/core/Title';
import { ExistingDocumentationFieldArray } from '@components/grievances/Documentation/ExistingDocumentationFieldArray';
import { NewDocumentationFieldArray } from '@components/grievances/Documentation/NewDocumentationFieldArray';
import { LookUpLinkedTickets } from '@components/grievances/LookUps/LookUpLinkedTickets/LookUpLinkedTickets';
import { LookUpPaymentRecord } from '@components/grievances/LookUps/LookUpPaymentRecord/LookUpPaymentRecord';
import { OtherRelatedTicketsCreate } from '@components/grievances/OtherRelatedTicketsCreate';
import {
  getGrievanceDetailsPath,
  selectedIssueType,
} from '@components/grievances/utils/createGrievanceUtils';
import {
  EmptyComponent,
  dataChangeComponentDict,
  prepareInitialValues,
  prepareVariables,
} from '@components/grievances/utils/editGrievanceUtils';
import { validate } from '@components/grievances/utils/validateGrievance';
import { validationSchema } from '@components/grievances/utils/validationSchema';
import {
  PERMISSIONS,
  hasCreatorOrOwnerPermissions,
  hasPermissions,
} from '../../../config/permissions';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { FormikAdminAreaAutocomplete } from '@shared/Formik/FormikAdminAreaAutocomplete';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import {
  getGrievanceCategoryDescriptions,
  getGrievanceIssueTypeDescriptions,
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_CATEGORIES_NAMES,
  GRIEVANCE_ISSUE_TYPES,
  GRIEVANCE_ISSUE_TYPES_NAMES,
  GRIEVANCE_TICKET_STATES,
} from '@utils/constants';
import {
  choicesToDict,
  isInvalid,
  isPermissionDeniedError,
  thingForSpecificGrievanceType,
} from '@utils/utils';
import { grievancePermissions } from './GrievancesDetailsPage/grievancePermissions';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

const BoxPadding = styled.div`
  padding: 15px 0;
`;
const NewTicket = styled.div`
  padding: 20px;
`;

const BoxWithBottomBorders = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

const EditGrievancePage = (): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { baseUrl, businessArea, isAllPrograms } = useBaseUrl();
  const { selectedProgram, isSocialDctType } = useProgramContext();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const { id } = useParams();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

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

  const { data: currentUserData, loading: currentUserDataLoading } =
    useMeQuery();

  const { data: choicesData, loading: choicesLoading } =
    useGrievancesChoiceDataQuery();

  const [mutate, { loading }] = useUpdateGrievanceMutation();
  const [mutateStatus] = useGrievanceTicketStatusChangeMutation();
  const {
    data: allAddIndividualFieldsData,
    loading: allAddIndividualFieldsDataLoading,
  } = useAllAddIndividualFieldsQuery();
  const { data: householdFieldsData, loading: householdFieldsLoading } =
    useAllEditHouseholdFieldsQuery();
  const { data: allEditPeopleFieldsData, loading: allEditPeopleFieldsLoading } =
    useAllEditPeopleFieldsQuery();

  const { data: programsData, loading: programsDataLoading } =
    useAllProgramsForChoicesQuery({
      variables: {
        first: 100,
        businessArea,
      },
    });
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

  const peopleFieldsDict = useArrayToDict(
    allEditPeopleFieldsData?.allEditPeopleFieldsAttributes,
    'name',
    '*',
  );

  if (
    choicesLoading ||
    ticketLoading ||
    allAddIndividualFieldsDataLoading ||
    allEditPeopleFieldsLoading ||
    householdFieldsLoading ||
    currentUserDataLoading ||
    programsDataLoading
  )
    return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (
    !choicesData ||
    !ticketData ||
    !currentUserData ||
    permissions === null ||
    !householdFieldsData ||
    !householdFieldsDict ||
    !individualFieldsDict ||
    !peopleFieldsDict ||
    !programsData
  )
    return null;

  const categoryChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.grievanceTicketCategoryChoices);

  const currentUserId = currentUserData.me.id;
  const ticket = ticketData.grievanceTicket;

  const isCreator = ticket.createdBy?.id === currentUserId;
  const isOwner = ticket.assignedTo?.id === currentUserId;

  const { canViewHouseholdDetails, canViewIndividualDetails } =
    grievancePermissions(isCreator, isOwner, ticket, permissions);

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
      to: getGrievanceDetailsPath(ticket.id, ticket.category, baseUrl),
    },
  ];

  const showIssueType = (values): boolean =>
    values.category ===
      parseInt(GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE, 10) ||
    values.category === parseInt(GRIEVANCE_CATEGORIES.DATA_CHANGE, 10) ||
    values.category === parseInt(GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT, 10);
  const dataChangeErrors = (errors, touched): ReactElement[] =>
    [
      'householdDataUpdateFields',
      'individualDataUpdateFields',
      'individualDataUpdateFieldsDocuments',
      'individualDataUpdateFieldsIdentities',
      'individualDataUpdateDocumentsToEdit',
      'individualDataUpdateIdentitiesToEdit',
      'individualDataUpdateFieldsAccounts',
      'individualDataUpdateAccountsToEdit',
      'peopleDataUpdateFields',
    ].map(
      (fieldname) =>
        isInvalid(fieldname, errors, touched) && (
          <FormHelperText key={errors[fieldname]} error>
            {errors[fieldname]}
          </FormHelperText>
        ),
    );

  const canAddDocumentation = hasPermissions(
    PERMISSIONS.GRIEVANCE_DOCUMENTS_UPLOAD,
    permissions,
  );

  const grievanceDetailsPath = getGrievanceDetailsPath(
    ticket.id,
    ticket.category,
    baseUrl,
  );

  const mappedProgramChoices = programsData?.allPrograms?.edges?.map(
    (element) => ({ name: element.node.name, value: element.node.id }),
  );

  const accountsToEdit =
    ticket?.individualDataUpdateTicketDetails?.individualData
      ?.accounts_to_edit;


  const individualFieldsDictForValidation = isSocialDctType
    ? peopleFieldsDict
    : individualFieldsDict;

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
          showMessage(t('Grievance Ticket edited.'));
          navigate(grievanceDetailsPath);
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
          individualFieldsDictForValidation,
          householdFieldsDict,
          beneficiaryGroup,
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
        const categoryDescriptions =
          getGrievanceCategoryDescriptions(beneficiaryGroup);
        const issueTypeDescriptions =
          getGrievanceIssueTypeDescriptions(beneficiaryGroup);

        const categoryDescription =
          categoryDescriptions[GRIEVANCE_CATEGORIES_NAMES[values.category]] ||
          '';
        const issueTypeDescription =
          issueTypeDescriptions[
            GRIEVANCE_ISSUE_TYPES_NAMES[values.issueType]
          ] || '';

        return (
          <>
            <AutoSubmitFormOnEnter />
            <PageHeader
              title={`${t('Edit Ticket')} #${ticket.unicefId}`}
              breadCrumbs={breadCrumbsItems}
            >
              <Box display="flex" alignContent="center">
                <Box mr={3}>
                  <Button component={Link} to={grievanceDetailsPath}>
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
                <NewTicket>
                  <ContainerColumnWithBorder>
                    <Grid container spacing={3}>
                      <Grid size={{ xs: 3 }}>
                        <LabelizedField label={t('Category')}>
                          {categoryChoices[ticket.category]}
                        </LabelizedField>
                      </Grid>
                      {showIssueType(values) ? (
                        <Grid size={{ xs: 6 }}>
                          <LabelizedField label={t('Issue Type')}>
                            {selectedIssueType(
                              values,
                              choicesData.grievanceTicketIssueTypeChoices,
                            )}
                          </LabelizedField>
                        </Grid>
                      ) : null}
                      {values.category && (
                        <>
                          <DividerLine />
                          <Grid size={{ xs: 6 }}>
                            <LabelizedField label={t('Category Description')}>
                              {categoryDescription}
                            </LabelizedField>
                          </Grid>
                          {issueTypeDescription && (
                            <Grid size={{ xs: 6 }}>
                              <LabelizedField
                                label={t('Issue Type Description')}
                              >
                                {issueTypeDescription}
                              </LabelizedField>
                            </Grid>
                          )}
                          <DividerLine />
                        </>
                      )}
                      <Grid container size={{ xs: 12 }}>
                        <Grid size={{ xs: 3 }}>
                          <LabelizedField
                            label={`${beneficiaryGroup?.groupLabel}`}
                          >
                            <span>
                              {ticket.household?.id &&
                              canViewHouseholdDetails &&
                              !isAllPrograms ? (
                                <BlackLink
                                  to={`/${baseUrl}/population/household/${ticket.household.id}`}
                                >
                                  {ticket.household.unicefId}
                                </BlackLink>
                              ) : (
                                <div>
                                  {ticket.household?.id
                                    ? ticket.household.unicefId
                                    : '-'}
                                </div>
                              )}
                            </span>
                          </LabelizedField>
                        </Grid>
                        <Grid size={{ xs: 3 }}>
                          <LabelizedField label={t('Individual ID')}>
                            <span>
                              {ticket.individual?.id &&
                              canViewIndividualDetails &&
                              !isAllPrograms ? (
                                <BlackLink
                                  to={`/${baseUrl}/population/individuals/${ticket.individual.id}`}
                                >
                                  {ticket.individual.unicefId}
                                </BlackLink>
                              ) : (
                                <div>
                                  {ticket.individual?.id
                                    ? ticket.individual.unicefId
                                    : '-'}
                                </div>
                              )}
                            </span>
                          </LabelizedField>
                        </Grid>
                      </Grid>
                    </Grid>
                    <BoxPadding>
                      <Grid container spacing={3}>
                        <Grid size={{ xs: 12 }}>
                          <Field
                            name="description"
                            multiline
                            fullWidth
                            disabled={Boolean(ticket.description)}
                            variant="outlined"
                            label="Description"
                            required
                            component={FormikTextField}
                          />
                        </Grid>
                        <Grid size={{ xs: 12 }}>
                          <Field
                            name="comments"
                            multiline
                            fullWidth
                            disabled={Boolean(ticket.comments)}
                            variant="outlined"
                            label="Comments"
                            component={FormikTextField}
                          />
                        </Grid>
                        <Grid size={{ xs: 6 }}>
                          <Field
                            name="admin"
                            disabled={Boolean(ticket.admin)}
                            variant="outlined"
                            component={FormikAdminAreaAutocomplete}
                          />
                        </Grid>
                        <Grid size={{ xs: 6 }}>
                          <Field
                            name="area"
                            fullWidth
                            disabled={Boolean(ticket.area)}
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
                            disabled={Boolean(ticket.language)}
                            variant="outlined"
                            label={t('Languages Spoken')}
                            component={FormikTextField}
                          />
                        </Grid>
                        <Grid size={{ xs: 3 }}>
                          <Field
                            name="priority"
                            multiline
                            fullWidth
                            variant="outlined"
                            label={t('Priority')}
                            choices={choicesData.grievanceTicketPriorityChoices}
                            component={FormikSelectField}
                          />
                        </Grid>
                        <Grid size={{ xs: 3 }}>
                          <Field
                            name="urgency"
                            multiline
                            fullWidth
                            variant="outlined"
                            label={t('Urgency')}
                            choices={choicesData.grievanceTicketUrgencyChoices}
                            component={FormikSelectField}
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
                              !isAllPrograms ||
                              Boolean(ticket.programs?.[0]?.id)
                            }
                          />
                        </Grid>
                      </Grid>
                      {canAddDocumentation && (
                        <Box mt={3}>
                          <Title>
                            <Typography variant="h6">
                              {t(
                                'Grievance Supporting Documents: upload of document: support documentation for the ticket',
                              )}
                            </Typography>
                          </Title>
                          <ExistingDocumentationFieldArray
                            values={values}
                            setFieldValue={setFieldValue}
                            errors={errors}
                            ticket={ticket}
                          />
                          <NewDocumentationFieldArray
                            values={values}
                            setFieldValue={setFieldValue}
                            errors={errors}
                          />
                        </Box>
                      )}
                    </BoxPadding>
                    <BoxPadding>
                      <Grid size={{ xs: 6 }}>
                        <Box py={3}>
                          <LookUpLinkedTickets
                            values={values}
                            onValueChange={setFieldValue}
                            disabled={Boolean(ticket.linkedTickets)}
                          />
                        </Box>
                      </Grid>
                      {(ticket.issueType?.toString() ===
                        GRIEVANCE_ISSUE_TYPES.PAYMENT_COMPLAINT ||
                        ticket.issueType?.toString() ===
                          GRIEVANCE_ISSUE_TYPES.FSP_COMPLAINT) && (
                        <BoxWithBottomBorders>
                          <Grid size={{ xs: 6 }}>
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
                      <>
                        <BoxPadding>
                          <DataChangeComponent
                            values={values}
                            setFieldValue={setFieldValue}
                          />
                          {dataChangeErrors(errors, touched)}
                        </BoxPadding>
                        <BoxPadding>
                          {accountsToEdit && (
                            <>
                              <Title>
                                <Typography variant="h6">
                                  {t('Accounts to Edit')}
                                </Typography>
                              </Title>
                              <Grid container spacing={3}>
                                {values.individualDataUpdateAccountsToEdit?.map(
                                  (
                                    item: {
                                      id: string;
                                      label: string;
                                      dataFields: Record<
                                        string,
                                        {
                                          name: string;
                                          previousValue: string;
                                          value: string;
                                        }
                                      >;
                                    },
                                    index: number,
                                  ) => (
                                    <Grid
                                      item
                                      size={{ xs: 12 }}
                                      key={item.id}
                                    >
                                      <Typography variant="subtitle1">
                                        Account: {item.name}
                                      </Typography>
                                      {Object.entries(item.dataFields).map(
                                        (
                                          [, field]: [
                                            string,
                                            {
                                              name: string;
                                              previousValue: string;
                                              value: string;
                                            },
                                          ],
                                          fieldIndex: number,
                                        ) => (
                                          <Grid
                                            key={field.name}
                                            container
                                            alignItems="flex-end"
                                            spacing={2}
                                          >
                                            <Grid size={{ xs: 4 }}>
                                              <LabelizedField
                                                label={t('Field Name')}
                                                fullWidth
                                              >
                                                {field.name}
                                              </LabelizedField>
                                            </Grid>
                                            <Grid size={{ xs: 4 }}>
                                              <Field
                                                name={`individualDataUpdateAccountsToEdit[${index}].dataFields[${fieldIndex}].previousValue`}
                                                type="text"
                                                label={t('Current Value')}
                                                component={FormikTextField}
                                                disabled
                                                fullWidth
                                              />
                                            </Grid>
                                            <Grid size={{ xs: 4 }}>
                                              <Field
                                                name={`individualDataUpdateAccountsToEdit[${index}].dataFields[${fieldIndex}].value`}
                                                type="text"
                                                label={t('New Value')}
                                                component={FormikTextField}
                                                required
                                                fullWidth
                                              />
                                            </Grid>
                                          </Grid>
                                        ),
                                      )}
                                    </Grid>
                                  ),
                                )}
                              </Grid>
                            </>
                          )}
                        </BoxPadding>
                      </>
                    )}
                  </ContainerColumnWithBorder>
                </NewTicket>
              </Grid>
              <Grid size={{ xs: 6 }}>
                <NewTicket>
                  <OtherRelatedTicketsCreate values={values} />
                </NewTicket>
              </Grid>
            </Grid>
          </>
        );
      }}
    </Formik>
  );
};

export default withErrorBoundary(EditGrievancePage, 'EditGrievancePage');
