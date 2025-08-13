import React, { ReactElement, useState } from 'react';
import { Formik, useFormikContext } from 'formik';
import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { LoadingButton } from '@components/core/LoadingButton';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import AddIndividualDataChange from '@components/grievances/AddIndividualDataChange';
import { CreateGrievanceStepper } from '@components/grievances/CreateGrievance/CreateGrievanceStepper/CreateGrievanceStepper';
import Description from '@components/grievances/CreateGrievance/Description/Description';
import Selection from '@components/grievances/CreateGrievance/Selection/Selection';
import Verification from '@components/grievances/CreateGrievance/Verification/Verification';
import EditHouseholdDataChange from '@components/grievances/EditHouseholdDataChange/EditHouseholdDataChange';
import EditIndividualDataChange from '@components/grievances/EditIndividualDataChange/EditIndividualDataChange';
import EditPeopleDataChange from '@components/grievances/EditPeopleDataChange/EditPeopleDataChange';
import { LookUpHouseholdIndividualSelection } from '@components/grievances/LookUps/LookUpHouseholdIndividual/LookUpHouseholdIndividualSelection';
import { OtherRelatedTicketsCreate } from '@components/grievances/OtherRelatedTicketsCreate';
import { TicketsAlreadyExist } from '@components/grievances/TicketsAlreadyExist';
import {
  getGrievanceDetailsPath,
  prepareRestVariables,
  selectedIssueType,
} from '@components/grievances/utils/createGrievanceUtils';
import { validateUsingSteps } from '@components/grievances/utils/validateGrievance';
import { validationSchemaWithSteps } from '@components/grievances/utils/validationSchema';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Button, FormHelperText, Grid2 as Grid } from '@mui/material';
import { CreateGrievanceTicket } from '@restgenerated/models/CreateGrievanceTicket';
import { PaginatedProgramListList } from '@restgenerated/models/PaginatedProgramListList';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
  GrievanceSteps,
} from '@utils/constants';
import {
  showApiErrorMessages,
  thingForSpecificGrievanceType,
} from '@utils/utils';
import { useTranslation } from 'react-i18next';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import {
  hasPermissionInModule,
  hasPermissions,
  PERMISSIONS,
} from '../../../config/permissions';

const InnerBoxPadding = styled.div`
  .MuiPaper-root {
    padding: 32px 20px;
  }
`;

const NewTicket = styled.div`
  padding: 20px;
`;

const BoxWithBorders = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

function EmptyComponent(): ReactElement {
  return null;
}

function FormikSelectedEntitiesSync({
  fetchedHousehold,
  fetchedIndividual,
}: {
  fetchedHousehold: any;
  fetchedIndividual: any;
}) {
  const { values, setFieldValue } = useFormikContext<any>();
  React.useEffect(() => {
    if (fetchedHousehold && values.selectedHousehold !== fetchedHousehold) {
      setFieldValue('selectedHousehold', fetchedHousehold);
    }
  }, [fetchedHousehold, values.selectedHousehold, setFieldValue]);
  React.useEffect(() => {
    if (fetchedIndividual && values.selectedIndividual !== fetchedIndividual) {
      setFieldValue('selectedIndividual', fetchedIndividual);
    }
  }, [fetchedIndividual, values.selectedIndividual, setFieldValue]);
  return null;
}

const CreateGrievancePage = (): ReactElement => {
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { baseUrl, businessArea, programId, isAllPrograms } = useBaseUrl();
  const { isSocialDctType } = useProgramContext();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const [activeStep, setActiveStep] = useState(GrievanceSteps.Selection);
  const [validateData, setValidateData] = useState(false);

  const dataChangeComponentDict = {
    [GRIEVANCE_CATEGORIES.DATA_CHANGE]: {
      [GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL]: AddIndividualDataChange,
      [GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL]: isSocialDctType
        ? EditPeopleDataChange
        : EditIndividualDataChange,
      [GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD]: EditHouseholdDataChange,
    },
  };

  const linkedTicketId = location.state?.linkedTicketId;
  const selectedHousehold = location.state?.selectedHousehold;

  // Fetch full household object if selectedHousehold is an ID (string/number)
  const shouldFetchHousehold = Boolean(
    selectedHousehold &&
      (typeof selectedHousehold === 'string' ||
        typeof selectedHousehold === 'number'),
  );
  const { data: fetchedHousehold, isLoading: fetchedHouseholdLoading } =
    useQuery({
      queryKey: ['household', businessArea, programId, selectedHousehold],
      queryFn: () =>
        RestService.restBusinessAreasProgramsHouseholdsRetrieve({
          businessAreaSlug: businessArea,
          programSlug: programId,
          id: String(selectedHousehold),
        }),
      enabled: shouldFetchHousehold,
    });
  const selectedIndividual = location.state?.selectedIndividual;

  // Fetch full individual object if selectedIndividual is an ID (string/number)
  const shouldFetchIndividual = Boolean(
    selectedIndividual &&
      (typeof selectedIndividual === 'string' ||
        typeof selectedIndividual === 'number'),
  );

  const { data: fetchedIndividual, isLoading: fetchedIndividualLoading } =
    useQuery({
      queryKey: ['individual', businessArea, programId, selectedIndividual],
      queryFn: () =>
        RestService.restBusinessAreasProgramsIndividualsRetrieve({
          businessAreaSlug: businessArea,
          programSlug: programId,
          id: String(selectedIndividual),
        }),
      enabled: shouldFetchIndividual,
    });
  const category = location.state?.category;
  const linkedFeedbackId = location.state?.linkedFeedbackId;
  const redirectedFromRelatedTicket = Boolean(category);
  const isFeedbackWithHouseholdOnly =
    location.state?.isFeedbackWithHouseholdOnly;

  const initialValues = {
    description: '',
    category: category || null,
    language: '',
    consent: false,
    admin: selectedHousehold?.admin2?.id || null,
    area: '',
    selectedHousehold: selectedHousehold || null,
    selectedIndividual: selectedIndividual || null,
    selectedPaymentRecords: [],
    selectedLinkedTickets: linkedTicketId ? [linkedTicketId] : [],
    identityVerified: false,
    issueType: null,
    priority: null,
    urgency: null,
    partner: null,
    program: isAllPrograms ? '' : programId,
    comments: null,
    linkedFeedbackId: linkedFeedbackId || null,
    documentation: [],
    individualDataUpdateFields: [{ fieldName: null, fieldValue: null }],
    roles: [],
  };

  const { data: choicesData, isLoading: choicesLoading } = useQuery<any>({
    queryKey: ['businessAreasGrievanceTicketsChoices', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
        businessAreaSlug: businessArea,
      }),
  });

  const { mutateAsync, isPending: loading } = useMutation({
    mutationFn: (requestData: CreateGrievanceTicket) => {
      return RestService.restBusinessAreasGrievanceTicketsCreate({
        businessAreaSlug: businessArea,
        formData: requestData as any,
      });
    },
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

  const {
    data: allAddIndividualFieldsData,
    isLoading: allAddIndividualFieldsDataLoading,
  } = useQuery({
    queryKey: ['addIndividualFieldsAttributes', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsAllAddIndividualsFieldsAttributesList(
        {
          businessAreaSlug: businessArea,
        },
      ),
  });

  const { data: householdFieldsData, isLoading: householdFieldsLoading } =
    useQuery({
      queryKey: ['householdFieldsAttributes', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasGrievanceTicketsAllEditHouseholdFieldsAttributesList(
          {
            businessAreaSlug: businessArea,
          },
        ),
    });

  const {
    data: allEditPeopleFieldsData,
    isLoading: allEditPeopleFieldsLoading,
  } = useQuery({
    queryKey: ['editPeopleFieldsAttributes', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsAllEditPeopleFieldsAttributesList(
        {
          businessAreaSlug: businessArea,
        },
      ),
  });

  const individualFieldsDict = useArrayToDict(
    //@ts-ignore
    allAddIndividualFieldsData,
    'name',
    '*',
  );

  const householdFieldsDict = useArrayToDict(
    //@ts-ignore
    householdFieldsData,
    'name',
    '*',
  );

  const peopleFieldsDict = useArrayToDict(
    //@ts-ignore
    allEditPeopleFieldsData,
    'name',
    '*',
  );

  const issueTypeDict = useArrayToDict(
    choicesData?.grievanceTicketIssueTypeChoices,
    'category',
    '*',
  );

  const individualFieldsDictForValidation = isSocialDctType
    ? peopleFieldsDict
    : individualFieldsDict;

  const showIssueType = (values): boolean =>
    values.category?.toString() === GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE ||
    values.category?.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE ||
    values.category?.toString() === GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT;
  if (
    choicesLoading ||
    allAddIndividualFieldsDataLoading ||
    householdFieldsLoading ||
    programsDataLoading ||
    allEditPeopleFieldsLoading ||
    (fetchedIndividualLoading && shouldFetchIndividual) ||
    fetchedHouseholdLoading
  )
    return <LoadingComponent />;
  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.GRIEVANCES_CREATE, permissions))
    return <PermissionDenied />;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Grievance and Feedback'),
      to: `/${baseUrl}/grievance/tickets/`,
    },
  ];

  const dataChangeErrors = (errors): ReactElement[] =>
    [
      'householdDataUpdateFields',
      'individualDataUpdateFields',
      'individualDataUpdateFieldsDocuments',
      'individualDataUpdateFieldsIdentities',
      'individualDataUpdateFieldsAccounts',
      'individualDataUpdateAccountsToEdit',
      'verificationRequired',
    ].map((fieldname) => (
      <FormHelperText key={fieldname} error>
        {errors[fieldname]}
      </FormHelperText>
    ));

  const handleNext = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = (): void => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  let steps = isSocialDctType
    ? [
        'Category Selection',
        `${beneficiaryGroup?.memberLabel} Look up`,
        'Identity Verification',
        'Description',
      ]
    : [
        'Category Selection',
        `${beneficiaryGroup?.groupLabel}/${beneficiaryGroup?.memberLabel} Look up`,
        'Identity Verification',
        'Description',
      ];

  // if creating a linked G&F ticket from Feedback page skip Look Up
  if (linkedFeedbackId && selectedHousehold && selectedIndividual) {
    steps = ['Category Selection', 'Identity Verification', 'Description'];
  }

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        if (activeStep === GrievanceSteps.Description) {
          try {
            const requestData = prepareRestVariables(businessArea, values);
            const data = await mutateAsync(requestData);
            const grievanceTickets = data || [];
            const grievanceTicket = grievanceTickets[0];
            let msg: string;
            let url: string;
            const paymentsNumber = values.selectedPaymentRecords.length;
            if (paymentsNumber > 1) {
              msg = `${paymentsNumber} ${t('Grievance Tickets created')}.`;
              url = `/${baseUrl}/grievance/tickets/user-generated`;
            } else {
              msg = t('Grievance Ticket created.');
              url = getGrievanceDetailsPath(
                grievanceTicket.id,
                grievanceTicket.category,
                baseUrl,
              );
            }
            showMessage(msg);
            navigate(url);
          } catch (e) {
            showApiErrorMessages(
              e,
              showMessage,
              'An error occurred while creating the grievance ticket',
            );
          }
        } else {
          setValidateData(false);
          handleNext();
          // if creating a linked G&F ticket from Feedback page and IND and HH selected skip Look Up
          if (
            activeStep === 0 &&
            linkedFeedbackId &&
            selectedHousehold &&
            selectedIndividual
          ) {
            handleNext();
          }
        }
      }}
      validateOnChange={
        activeStep < GrievanceSteps.Verification || validateData
      }
      validateOnBlur={activeStep < GrievanceSteps.Verification || validateData}
      validate={(values) =>
        validateUsingSteps(
          values,
          allAddIndividualFieldsData || null,
          individualFieldsDictForValidation,
          householdFieldsDict,
          activeStep,
          setValidateData,
          beneficiaryGroup,
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
        const DataChangeComponent = thingForSpecificGrievanceType(
          values,
          dataChangeComponentDict,
          EmptyComponent,
        );

        const getIssueTypeToDisplay = (): string => {
          if (!values.issueType) return '';
          return selectedIssueType(values, issueTypeDict);
        };

        const issueTypeToDisplay = getIssueTypeToDisplay();

        const disableNextOnFirstStep = (): boolean => {
          if (!values.category) return true;
          if (showIssueType(values)) {
            if (!values.issueType) return true;
          }
          return false;
        };

        return (
          <>
            <FormikSelectedEntitiesSync
              fetchedHousehold={
                shouldFetchHousehold
                  ? fetchedHousehold
                  : values.selectedHousehold
              }
              fetchedIndividual={
                shouldFetchIndividual
                  ? fetchedIndividual
                  : values.selectedIndividual
              }
            />
            <AutoSubmitFormOnEnter />
            <PageHeader
              title="New Ticket"
              breadCrumbs={
                hasPermissionInModule('GRIEVANCES_VIEW_LIST', permissions)
                  ? breadCrumbsItems
                  : null
              }
            />
            <Grid container spacing={3}>
              <Grid size={{ xs: 12 }}>
                <NewTicket>
                  <InnerBoxPadding>
                    <ContainerColumnWithBorder>
                      <CreateGrievanceStepper
                        activeStep={activeStep}
                        steps={steps}
                      />
                      {activeStep === GrievanceSteps.Selection && (
                        <Selection
                          handleChange={handleChange}
                          choicesData={choicesData}
                          setFieldValue={setFieldValue}
                          showIssueType={showIssueType}
                          values={values}
                          redirectedFromRelatedTicket={
                            redirectedFromRelatedTicket
                          }
                        />
                      )}
                      {activeStep === GrievanceSteps.Lookup && (
                        <BoxWithBorders>
                          <Box display="flex" flexDirection="column">
                            <LookUpHouseholdIndividualSelection
                              values={values}
                              onValueChange={setFieldValue}
                              errors={errors}
                              touched={touched}
                              redirectedFromRelatedTicket={
                                redirectedFromRelatedTicket
                              }
                              isFeedbackWithHouseholdOnly={
                                isFeedbackWithHouseholdOnly
                              }
                            />
                          </Box>
                        </BoxWithBorders>
                      )}
                      {activeStep === GrievanceSteps.Verification && (
                        <Verification values={values} />
                      )}
                      {activeStep === GrievanceSteps.Description && (
                        <>
                          <Description
                            values={values}
                            showIssueType={showIssueType}
                            issueTypeToDisplay={issueTypeToDisplay}
                            baseUrl={baseUrl}
                            choicesData={choicesData}
                            programsData={programsData}
                            setFieldValue={setFieldValue}
                            errors={errors}
                            permissions={permissions}
                          />
                          <DataChangeComponent
                            values={values}
                            setFieldValue={setFieldValue}
                          />
                        </>
                      )}
                      {dataChangeErrors(errors)}
                      <Box pt={3} display="flex" flexDirection="row">
                        <Box mr={3}>
                          <Button
                            component={Link}
                            to={`/${baseUrl}/grievance/tickets/user-generated`}
                          >
                            {t('Cancel')}
                          </Button>
                        </Box>
                        <Box display="flex" ml="auto">
                          <Button
                            disabled={activeStep === 0}
                            onClick={handleBack}
                          >
                            {t('Back')}
                          </Button>
                          <LoadingButton
                            loading={loading}
                            color="primary"
                            variant="contained"
                            onClick={submitForm}
                            data-cy="button-submit"
                            disabled={disableNextOnFirstStep()}
                          >
                            {activeStep === GrievanceSteps.Description
                              ? t('Save')
                              : t('Next')}
                          </LoadingButton>
                        </Box>
                      </Box>
                    </ContainerColumnWithBorder>
                  </InnerBoxPadding>
                </NewTicket>
              </Grid>
              {activeStep === GrievanceSteps.Selection && (
                <Grid size={{ xs: 12 }}>
                  <NewTicket>
                    <Grid container spacing={3}>
                      <TicketsAlreadyExist values={values} />
                      <Grid size={{ xs: 6 }}>
                        <OtherRelatedTicketsCreate values={values} />
                      </Grid>
                    </Grid>
                  </NewTicket>
                </Grid>
              )}
            </Grid>
          </>
        );
      }}
    </Formik>
  );
};

export default withErrorBoundary(CreateGrievancePage, 'CreateGrievancePage');
