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
import withErrorBoundary from '@components/core/withErrorBoundary';
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
  prepareRestUpdateVariables,
} from '@components/grievances/utils/editGrievanceUtils';
import { validate } from '@components/grievances/utils/validateGrievance';
import { validationSchema } from '@components/grievances/utils/validationSchema';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  FormHelperText,
  Grid2 as Grid,
  Typography,
} from '@mui/material';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { PaginatedProgramListList } from '@restgenerated/models/PaginatedProgramListList';
import { RestService } from '@restgenerated/services/RestService';
import { FormikAdminAreaAutocomplete } from '@shared/Formik/FormikAdminAreaAutocomplete';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_CATEGORIES_NAMES,
  GRIEVANCE_ISSUE_TYPES,
  GRIEVANCE_ISSUE_TYPES_NAMES,
  GRIEVANCE_TICKET_STATES,
  getGrievanceCategoryDescriptions,
  getGrievanceIssueTypeDescriptions,
} from '@utils/constants';
import {
  choicesToDict,
  isInvalid,
  isPermissionDeniedError,
  thingForSpecificGrievanceType,
} from '@utils/utils';
import { Field, Formik } from 'formik';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import {
  PERMISSIONS,
  hasCreatorOrOwnerPermissions,
  hasPermissions,
} from '../../../config/permissions';
import { grievancePermissions } from './GrievancesDetailsPage/grievancePermissions';

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
  const { baseUrl, businessAreaSlug, programSlug, isAllPrograms } =
    useBaseUrl();
  const { selectedProgram, isSocialDctType } = useProgramContext();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const { id } = useParams();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const queryClient = useQueryClient();

  const {
    data: ticketData,
    isLoading: ticketLoading,
    error,
  } = useQuery<GrievanceTicketDetail>({
    queryKey: ['businessAreaProgram', businessAreaSlug, id],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsRetrieve({
        businessAreaSlug,
        id: id,
      }),
  });

  const { data: currentUserData, isLoading: currentUserDataLoading } = useQuery(
    {
      queryKey: ['profile', businessAreaSlug, programSlug],
      queryFn: () => {
        return RestService.restBusinessAreasUsersProfileRetrieve({
          businessAreaSlug,
          program: programSlug === 'all' ? undefined : programSlug,
        });
      },
      staleTime: 5 * 60 * 1000, // Data is considered fresh for 5 minutes
      gcTime: 30 * 60 * 1000, // Keep unused data in cache for 30 minutes
      refetchOnWindowFocus: false, // Don't refetch when window regains focus
    },
  );

  const { data: choicesData, isLoading: choicesLoading } = useQuery({
    queryKey: ['businessAreasGrievanceTicketsChoices', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
        businessAreaSlug,
      }),
  });

  const { mutateAsync: updateGrievanceTicket, isPending: loading } =
    useMutation({
      mutationFn: (data: { id: string; requestBody: any }) =>
        RestService.restBusinessAreasGrievanceTicketsPartialUpdate({
          businessAreaSlug,
          id: data.id,
          requestBody: data.requestBody,
        }),
    });

  const { mutateAsync: changeTicketStatus } = useMutation({
    mutationFn: (data: { id: string; requestBody: any }) =>
      RestService.restBusinessAreasGrievanceTicketsStatusChangeCreate({
        businessAreaSlug,
        id: data.id,
        requestBody: data.requestBody,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [
          'businessAreasGrievanceTicketsRetrieve',
          businessAreaSlug,
          id,
        ],
      });
    },
  });

  const {
    data: allAddIndividualFieldsData,
    isLoading: allAddIndividualFieldsDataLoading,
  } = useQuery({
    queryKey: ['addIndividualFieldsAttributes', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsAllAddIndividualsFieldsAttributesList(
        {
          businessAreaSlug,
        },
      ),
  });
  const { data: householdFieldsData, isLoading: householdFieldsLoading } =
    useQuery({
      queryKey: ['householdFieldsAttributes', businessAreaSlug],
      queryFn: () =>
        RestService.restBusinessAreasGrievanceTicketsAllEditHouseholdFieldsAttributesList(
          {
            businessAreaSlug,
          },
        ),
    });
  const {
    data: allEditPeopleFieldsData,
    isLoading: allEditPeopleFieldsLoading,
  } = useQuery({
    queryKey: ['editPeopleFieldsAttributes', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsAllEditPeopleFieldsAttributesList(
        {
          businessAreaSlug,
        },
      ),
  });

  const { data: programsData, isLoading: programsDataLoading } =
    useQuery<PaginatedProgramListList>({
      queryKey: ['businessAreasProgramsList', { first: 100 }, businessAreaSlug],
      queryFn: () =>
        RestService.restBusinessAreasProgramsList(
          createApiParams(
            { businessAreaSlug, first: 100 },
            {
              withPagination: false,
            },
          ),
        ),
    });
  const individualFieldsDict = useArrayToDict(
    allAddIndividualFieldsData?.results,
    'name',
    '*',
  );
  const householdFieldsDict = useArrayToDict(
    householdFieldsData?.results,
    'name',
    '*',
  );

  const peopleFieldsDict = useArrayToDict(
    allEditPeopleFieldsData?.results,
    'name',
    '*',
  );

  const issueTypeDict = useArrayToDict(
    choicesData?.grievanceTicketIssueTypeChoices,
    'category',
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
  const categoryChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.grievanceTicketCategoryChoices);

  const currentUserId = currentUserData.id;
  const ticket = ticketData;

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

  const changeState = async (status): Promise<void> => {
    try {
      await changeTicketStatus({
        id: ticket.id,
        requestBody: {
          status,
        },
      });
      showMessage(t('Ticket status updated successfully.'));
    } catch (e) {
      if (e?.response?.data?.message) {
        showMessage(e.response.data.message);
      } else {
        showMessage(t('An error occurred while updating the ticket status.'));
      }
    }
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
      'individualDataUpdateFieldsPaymentChannels',
      'individualDataUpdatePaymentChannelsToEdit',
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

  const mappedProgramChoices = programsData?.results?.map((element) => ({
    name: element.name,
    value: element.id,
  }));

  const individualFieldsDictForValidation = isSocialDctType
    ? peopleFieldsDict
    : individualFieldsDict;

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        try {
          const requestBody = prepareRestUpdateVariables(values, ticket);
          await updateGrievanceTicket({
            id: ticket.id,
            requestBody,
          });
          showMessage(t('Grievance Ticket edited.'));
          navigate(grievanceDetailsPath);
        } catch (e) {
          if (e?.response?.data?.message) {
            showMessage(e.response.data.message);
          } else {
            showMessage(t('An error occurred while updating the ticket.'));
          }
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
          allAddIndividualFieldsData?.results || null,
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
                            {selectedIssueType(values, issueTypeDict)}
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
