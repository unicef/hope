import { Box, Button, FormHelperText, Grid } from '@material-ui/core';
import { Formik } from 'formik';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { ContainerColumnWithBorder } from '../../../components/core/ContainerColumnWithBorder';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { AddIndividualDataChange } from '../../../components/grievances/AddIndividualDataChange';
import { CreateGrievanceStepper } from '../../../components/grievances/CreateGrievance/CreateGrievanceStepper/CreateGrievanceStepper';
import { Description } from '../../../components/grievances/CreateGrievance/Description/Description';
import { Selection } from '../../../components/grievances/CreateGrievance/Selection/Selection';
import { Verification } from '../../../components/grievances/CreateGrievance/Verification/Verification';
import { EditHouseholdDataChange } from '../../../components/grievances/EditHouseholdDataChange/EditHouseholdDataChange';
import { EditIndividualDataChange } from '../../../components/grievances/EditIndividualDataChange/EditIndividualDataChange';
import { LookUpHouseholdIndividualSelection } from '../../../components/grievances/LookUps/LookUpHouseholdIndividual/LookUpHouseholdIndividualSelection';
import { OtherRelatedTicketsCreate } from '../../../components/grievances/OtherRelatedTicketsCreate';
import { TicketsAlreadyExist } from '../../../components/grievances/TicketsAlreadyExist';
import { prepareVariables } from '../../../components/grievances/utils/createGrievanceUtils';
import { validateUsingSteps } from '../../../components/grievances/utils/validateGrievance';
import { validationSchemaWithSteps } from '../../../components/grievances/utils/validationSchema';
import {
  hasPermissionInModule,
  hasPermissions,
  PERMISSIONS,
} from '../../../config/permissions';
import { useArrayToDict } from '../../../hooks/useArrayToDict';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import {
  GrievanceSteps,
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
} from '../../../utils/constants';
import {
  decodeIdString,
  isInvalid,
  thingForSpecificGrievanceType,
} from '../../../utils/utils';
import {
  useAllAddIndividualFieldsQuery,
  useAllEditHouseholdFieldsQuery,
  useAllProgramsQuery,
  useAllUsersQuery,
  useCreateGrievanceMutation,
  useGrievancesChoiceDataQuery,
  useUserChoiceDataQuery,
} from '../../../__generated__/graphql';

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
const EmptyComponent = (): React.ReactElement => null;
export const dataChangeComponentDict = {
  [GRIEVANCE_CATEGORIES.DATA_CHANGE]: {
    [GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL]: AddIndividualDataChange,
    [GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL]: EditIndividualDataChange,
    [GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD]: EditHouseholdDataChange,
  },
};

export const CreateGrievancePage = (): React.ReactElement => {
  const { t } = useTranslation();
  const history = useHistory();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();

  const [activeStep, setActiveStep] = useState(GrievanceSteps.Selection);
  const [validateData, setValidateData] = useState(false);

  const linkedTicketId = history.location.state?.linkedTicketId;
  const selectedHousehold = history.location.state?.selectedHousehold;
  const selectedIndividual = history.location.state?.selectedIndividual;
  const category = history.location.state?.category;
  const linkedFeedbackId = history.location.state?.linkedFeedbackId;

  const initialValues = {
    description: '',
    category: category || null,
    language: '',
    consent: false,
    admin: null,
    area: '',
    selectedHousehold: selectedHousehold || null,
    selectedIndividual: selectedIndividual || null,
    selectedPaymentRecords: [],
    selectedRelatedTickets: linkedTicketId ? [linkedTicketId] : [],
    identityVerified: false,
    issueType: null,
    priority: 3,
    urgency: 3,
    partner: null,
    programme: null,
    comments: null,
    linkedFeedbackId: linkedFeedbackId
      ? decodeIdString(linkedFeedbackId)
      : null,
    documentation: [],
  };
  const { data: userData, loading: userDataLoading } = useAllUsersQuery({
    variables: { businessArea, first: 1000 },
  });

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();
  const { data: userChoices } = useUserChoiceDataQuery();
  const [mutate, { loading }] = useCreateGrievanceMutation();

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

  const showIssueType = (values): boolean => {
    return (
      values.category === GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE ||
      values.category === GRIEVANCE_CATEGORIES.DATA_CHANGE ||
      values.category === GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT
    );
  };

  if (
    userDataLoading ||
    choicesLoading ||
    allAddIndividualFieldsDataLoading ||
    householdFieldsLoading ||
    loadingPrograms
  )
    return <LoadingComponent />;
  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.GRIEVANCES_CREATE, permissions))
    return <PermissionDenied />;

  if (
    !choicesData ||
    !userData ||
    !allAddIndividualFieldsData ||
    !householdFieldsData ||
    !householdFieldsDict ||
    !individualFieldsDict
  )
    return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Grievance and Feedback'),
      to: `/${businessArea}/grievance-and-feedback/tickets/`,
    },
  ];

  const dataChangeErrors = (errors, touched): ReactElement[] =>
    [
      'householdDataUpdateFields',
      'individualDataUpdateFields',
      'individualDataUpdateFieldsDocuments',
      'individualDataUpdateFieldsIdentities',
      'verificationRequired',
    ]
      .filter(
        (fieldname) =>
          isInvalid(fieldname, errors, touched) ||
          fieldname === 'verificationRequired',
      )
      .map((fieldname) => (
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

  const selectedIssueType = (values): string => {
    return values.issueType
      ? choicesData.grievanceTicketIssueTypeChoices
          .filter((el) => el.category === values.category.toString())[0]
          .subCategories.filter(
            (el) => el.value === values.issueType.toString(),
          )[0].name
      : '-';
  };

  let steps = [
    'Category Selection',
    'Household/Individual Look up',
    'Identity Verification',
    'Description',
  ];
  // if creating a linked G&F ticket from Feedback page skip Look Up
  if (linkedFeedbackId) {
    steps = ['Category Selection', 'Identity Verification', 'Description'];
  }

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        if (activeStep === GrievanceSteps.Description) {
          try {
            const response = await mutate(
              prepareVariables(businessArea, values),
            );
            if (values.selectedPaymentRecords.length > 1) {
              showMessage(
                `${values.selectedPaymentRecords.length} ${t(
                  'Grievance Tickets created',
                )}.`,
                {
                  pathname: `/${businessArea}/grievance-and-feedback`,
                  historyMethod: 'push',
                },
              );
            } else {
              showMessage(t('Grievance Ticket created.'), {
                pathname: `/${businessArea}/grievance-and-feedback/${response.data.createGrievanceTicket.grievanceTickets[0].id}`,
                historyMethod: 'push',
              });
            }
          } catch (e) {
            e.graphQLErrors.map((x) => showMessage(x.message));
          }
        } else {
          setValidateData(false);
          handleNext();
          // if creating a linked G&F ticket from Feedback page skip Look Up
          if (activeStep === 0 && linkedFeedbackId) {
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
          individualFieldsDict,
          householdFieldsDict,
          activeStep,
          setValidateData,
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
        return (
          <>
            <PageHeader
              title='New Ticket'
              breadCrumbs={
                hasPermissionInModule('GRIEVANCES_VIEW_LIST', permissions)
                  ? breadCrumbsItems
                  : null
              }
            />
            <Grid container spacing={3}>
              <Grid item xs={12}>
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
                        />
                      )}
                      {activeStep === GrievanceSteps.Lookup && (
                        <BoxWithBorders>
                          <Box display='flex' flexDirection='column'>
                            <LookUpHouseholdIndividualSelection
                              values={values}
                              onValueChange={setFieldValue}
                              errors={errors}
                              touched={touched}
                            />
                          </Box>
                        </BoxWithBorders>
                      )}
                      {activeStep === GrievanceSteps.Verification && (
                        <Verification values={values} />
                      )}
                      {activeStep === GrievanceSteps.Description && (
                        <Description
                          values={values}
                          showIssueType={showIssueType}
                          selectedIssueType={selectedIssueType}
                          businessArea={businessArea}
                          choicesData={choicesData}
                          userChoices={userChoices}
                          mappedPrograms={mappedPrograms}
                          setFieldValue={setFieldValue}
                          errors={errors}
                          permissions={permissions}
                        />
                      )}
                      <DataChangeComponent
                        values={values}
                        setFieldValue={setFieldValue}
                      />
                      {dataChangeErrors(errors, touched)}
                      <Box pt={3} display='flex' flexDirection='row'>
                        <Box mr={3}>
                          <Button
                            component={Link}
                            to={`/${businessArea}/grievance-and-feedback/tickets`}
                          >
                            {t('Cancel')}
                          </Button>
                        </Box>
                        <Box display='flex' ml='auto'>
                          <Button
                            disabled={activeStep === 0}
                            onClick={handleBack}
                          >
                            {t('Back')}
                          </Button>
                          <LoadingButton
                            loading={loading}
                            color='primary'
                            variant='contained'
                            onClick={submitForm}
                            data-cy='button-submit'
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
                <Grid item xs={12}>
                  <NewTicket>
                    <Grid container spacing={3}>
                      <TicketsAlreadyExist values={values} />
                      <Grid item xs={6}>
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
