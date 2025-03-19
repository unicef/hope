import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { LoadingButton } from '@components/core/LoadingButton';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { CreateGrievanceStepper } from '@components/grievances/CreateGrievance/CreateGrievanceStepper/CreateGrievanceStepper';
import { LookUpHouseholdIndividualSelection } from '@components/grievances/LookUps/LookUpHouseholdIndividual/LookUpHouseholdIndividualSelection';
import { OtherRelatedTicketsCreate } from '@components/grievances/OtherRelatedTicketsCreate';
import { TicketsAlreadyExist } from '@components/grievances/TicketsAlreadyExist';
import {
  getGrievanceDetailsPath,
  prepareVariables,
  selectedIssueType,
} from '@components/grievances/utils/createGrievanceUtils';
import { validateUsingSteps } from '@components/grievances/utils/validateGrievance';
import { validationSchemaWithSteps } from '@components/grievances/utils/validationSchema';
import {
  useAllAddIndividualFieldsQuery,
  useAllEditHouseholdFieldsQuery,
  useAllEditPeopleFieldsQuery,
  useAllProgramsForChoicesQuery,
  useCreateGrievanceMutation,
  useGrievancesChoiceDataQuery,
} from '@generated/graphql';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box, Button, FormHelperText, Grid2 as Grid } from '@mui/material';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
  GrievanceSteps,
} from '@utils/constants';
import { decodeIdString, thingForSpecificGrievanceType } from '@utils/utils';
import { Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import {
  PERMISSIONS,
  hasPermissionInModule,
  hasPermissions,
} from '../../../config/permissions';
import { useProgramContext } from 'src/programContext';
import withErrorBoundary from '@components/core/withErrorBoundary';
import AddIndividualDataChange from '@components/grievances/AddIndividualDataChange';
import Verification from '@components/grievances/CreateGrievance/Verification/Verification';
import EditHouseholdDataChange from '@components/grievances/EditHouseholdDataChange/EditHouseholdDataChange';
import EditIndividualDataChange from '@components/grievances/EditIndividualDataChange/EditIndividualDataChange';
import EditPeopleDataChange from '@components/grievances/EditPeopleDataChange/EditPeopleDataChange';
import Selection from '@components/grievances/CreateGrievance/Selection/Selection';
import Description from '@components/grievances/CreateGrievance/Description/Description';

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
  const selectedIndividual = location.state?.selectedIndividual;
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
    linkedFeedbackId: linkedFeedbackId
      ? decodeIdString(linkedFeedbackId)
      : null,
    documentation: [],
    individualDataUpdateFields: [{ fieldName: null, fieldValue: null }],
  };

  const { data: choicesData, loading: choicesLoading } =
    useGrievancesChoiceDataQuery();

  const [mutate, { loading }] = useCreateGrievanceMutation();
  const { data: programsData, loading: programsDataLoading } =
    useAllProgramsForChoicesQuery({
      variables: {
        first: 100,
        businessArea,
      },
    });

  const {
    data: allAddIndividualFieldsData,
    loading: allAddIndividualFieldsDataLoading,
  } = useAllAddIndividualFieldsQuery();

  const { data: householdFieldsData, loading: householdFieldsLoading } =
    useAllEditHouseholdFieldsQuery();

  const { data: allEditPeopleFieldsData, loading: allEditPeopleFieldsLoading } =
    useAllEditPeopleFieldsQuery();

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

  const individualFieldsDictForValidation = isSocialDctType
    ? peopleFieldsDict
    : individualFieldsDict;

  const showIssueType = (values): boolean =>
    values.category === GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE ||
    values.category === GRIEVANCE_CATEGORIES.DATA_CHANGE ||
    values.category === GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT;

  if (
    choicesLoading ||
    allAddIndividualFieldsDataLoading ||
    householdFieldsLoading ||
    programsDataLoading ||
    allEditPeopleFieldsLoading
  )
    return <LoadingComponent />;
  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.GRIEVANCES_CREATE, permissions))
    return <PermissionDenied />;

  if (
    !choicesData ||
    !allAddIndividualFieldsData ||
    !householdFieldsData ||
    !householdFieldsDict ||
    !individualFieldsDict ||
    !programsData ||
    !peopleFieldsDict
  )
    return null;

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
            const { data } = await mutate(
              prepareVariables(businessArea, values),
            );
            const grievanceTicket =
              data.createGrievanceTicket.grievanceTickets[0];
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
            e.graphQLErrors.map((x) => showMessage(x.message));
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
          allAddIndividualFieldsData,
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

        const issueTypeToDisplay = (): string =>
          selectedIssueType(
            values,
            choicesData.grievanceTicketIssueTypeChoices,
          );

        const disableNextOnFirstStep = (): boolean => {
          if (!values.category) return true;
          if (showIssueType(values)) {
            if (!values.issueType) return true;
          }
          return false;
        };

        return (
          <>
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
                            selectedIssueType={issueTypeToDisplay}
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
