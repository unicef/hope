import React from 'react';
import { Link, useParams } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import { Field, Formik } from 'formik';
import { Box, Button, DialogActions, Grid } from '@material-ui/core';
import camelCase from 'lodash/camelCase';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { PageHeader } from '../PageHeader';
import { BreadCrumbsItem } from '../BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';
import {
  GrievanceTicketQuery,
  useAllUsersQuery,
  useCreateGrievanceMutation,
  useGrievancesChoiceDataQuery,
  useGrievanceTicketQuery,
} from '../../__generated__/graphql';
import { LoadingComponent } from '../LoadingComponent';
import { useSnackbar } from '../../hooks/useSnackBar';
import { FormikAdminAreaAutocomplete } from '../../shared/Formik/FormikAdminAreaAutocomplete';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
} from '../../utils/constants';
import {
  decodeIdString,
  renderUserName,
  thingForSpecificGrievanceType,
} from '../../utils/utils';
import { Consent } from './Consent';
import { LookUpSection } from './LookUpSection';
import { OtherRelatedTicketsCreate } from './OtherRelatedTicketsCreate';
import { AddIndividualDataChange } from './AddIndividualDataChange';
import { EditIndividualDataChange } from './EditIndividualDataChange';
import { EditHouseholdDataChange } from './EditHouseholdDataChange';

const BoxPadding = styled.div`
  padding: 15px 0;
`;
const NewTicket = styled.div`
  padding: 20px;
`;
const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
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

function prepareInitialValueAddIndividual(
  initialValuesArg,
  ticket: GrievanceTicketQuery['grievanceTicket'],
) {
  const initialValues = initialValuesArg;
  initialValues.selectedHousehold = ticket.household;
  const individualData = {
    ...ticket.addIndividualTicketDetails.individualData,
  };
  initialValues.individualData = Object.entries(individualData).reduce(
    (previousValue, currentValue: [string, { value: string }]) => {
      // eslint-disable-next-line no-param-reassign,prefer-destructuring
      previousValue[camelCase(currentValue[0])] = currentValue[1];
      return previousValue;
    },
    {},
  );
  return initialValues;
}
function prepareInitialValueEditIndividual(
  initialValuesArg,
  ticket: GrievanceTicketQuery['grievanceTicket'],
) {
  const initialValues = initialValuesArg;
  initialValues.selectedIndividual = ticket.individual;
  const individualData = {
    ...ticket.individualDataUpdateTicketDetails.individualData,
  };
  const documents = individualData?.documents;
  const documentsToRemove = individualData.documents_to_remove;
  delete individualData.documents;
  delete individualData.documents_to_remove;
  delete individualData.previous_documents;
  initialValues.individualDataUpdateFields = Object.entries(individualData).map(
    (entry: [string, { value: string }]) => ({
      fieldName: entry[0],
      fieldValue: entry[1].value,
    }),
  );
  initialValues.individualDataUpdateFieldsDocuments = documents.map(
    (item) => item.value,
  );
  initialValues.individualDataUpdateDocumentsToRemove = documentsToRemove.map(
    (item) => item.value,
  );
  return initialValues;
}
function prepareInitialValueEditHousehold(
  initialValuesArg,
  ticket: GrievanceTicketQuery['grievanceTicket'],
) {
  const initialValues = initialValuesArg;
  initialValues.selectedHousehold = ticket.household;
  const householdData = {
    ...ticket.householdDataUpdateTicketDetails.householdData,
  };
  initialValues.householdDataUpdateFields = Object.entries(householdData).map(
    (entry: [string, { value: string }]) => ({
      fieldName: entry[0],
      fieldValue: entry[1].value,
    }),
  );
  return initialValues;
}

const prepareInitialValueDict = {
  [GRIEVANCE_CATEGORIES.DATA_CHANGE]: {
    [GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL]: prepareInitialValueAddIndividual,
    [GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL]: prepareInitialValueEditIndividual,
    [GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD]: prepareInitialValueEditHousehold,
  },
};

function prepareInitialValues(ticket: GrievanceTicketQuery['grievanceTicket']) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let initialValues: { [id: string]: any } = {
    description: ticket.description || '',
    assignedTo: ticket.assignedTo.id || '',
    category: ticket.category || null,
    language: ticket.language || '',
    consent: ticket.consent || false,
    admin: ticket.admin || '',
    area: ticket.area || '',
    selectedHousehold: ticket.household || null,
    selectedIndividual: ticket.individual || null,
    selectedPaymentRecords: null, //add value here ?
    identityVerified: false,
    issueType: ticket.issueType || null,
  };
  const prepareInitialValueFunction = thingForSpecificGrievanceType(
    ticket,
    prepareInitialValueDict,
    (initialValue) => initialValue,
  );
  initialValues = prepareInitialValueFunction(initialValues, ticket);
  return initialValues;
}

export function EditGrievancePage(): React.ReactElement {
  const businessArea = useBusinessArea();
  const { showMessage } = useSnackbar();
  const { id } = useParams();

  const { data: ticketData, loading: ticketLoading } = useGrievanceTicketQuery({
    variables: {
      id,
    },
  });

  const { data: userData, loading: userDataLoading } = useAllUsersQuery({
    variables: { businessArea },
  });

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();

  const [mutate] = useCreateGrievanceMutation();

  if (userDataLoading || choicesLoading || ticketLoading) {
    return <LoadingComponent />;
  }
  if (!choicesData || !userData || !ticketData) return null;

  const ticket = ticketData?.grievanceTicket;
  const mappedLinkedTickets = ticketData?.grievanceTicket?.relatedTickets?.map(
    (edge) => edge.id,
  );

  const initialValues = prepareInitialValues(ticket);

  const validationSchema = Yup.object().shape({
    description: Yup.string().required('Description is required'),
    assignedTo: Yup.string().required('Assigned To is required'),
    category: Yup.string()
      .required('Category is required')
      .nullable(),
    admin: Yup.string(),
    area: Yup.string(),
    language: Yup.string().required('Language is required'),
    consent: Yup.bool().oneOf([true], 'Consent is required'),
    selectedPaymentRecords: Yup.array()
      .of(Yup.string())
      .nullable(),
    selectedRelatedTickets: Yup.array()
      .of(Yup.string())
      .nullable(),
  });

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Grievance and Feedback',
      to: `/${businessArea}/grievance-and-feedback/`,
    },
  ];

  const mappedIndividuals = userData.allUsers.edges.map((edge) => ({
    name: renderUserName(edge.node),
    value: edge.node.id,
  }));

  const issueTypeDict = choicesData.grievanceTicketIssueTypeChoices.reduce(
    (prev, curr) => {
      // eslint-disable-next-line no-param-reassign
      prev[curr.category] = curr;
      return prev;
    },
    {},
  );
  const prepareVariables = (category: string, values) => {
    const requiredVariables = {
      businessArea,
      description: values.description,
      assignedTo: values.assignedTo,
      category: parseInt(values.category, 10),
      consent: values.consent,
      language: values.language,
      admin: values.admin,
      area: values.area,
    };

    if (
      category ===
      (GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK ||
        GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK ||
        GRIEVANCE_CATEGORIES.REFERRAL)
    ) {
      return {
        variables: {
          input: {
            ...requiredVariables,
            linkedTickets: values.selectedRelatedTickets,
          },
        },
      };
    }
    if (category === GRIEVANCE_CATEGORIES.GRIEVANCE_COMPLAINT) {
      return {
        variables: {
          input: {
            ...requiredVariables,
            linkedTickets: values.selectedRelatedTickets,
            extras: {
              category: {
                grievanceComplaintTicketExtras: {
                  household: values.selectedHousehold?.id,
                  individual: values.selectedIndividual?.id,
                  paymentRecord: values.selectedPaymentRecords,
                },
              },
            },
          },
        },
      };
    }
    if (category === GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE) {
      return {
        variables: {
          input: {
            ...requiredVariables,
            issueType: values.issueType,
            linkedTickets: values.selectedRelatedTickets,
            extras: {
              category: {
                sensitiveGrievanceTicketExtras: {
                  household: values.selectedHousehold?.id,
                  individual: values.selectedIndividual?.id,
                  paymentRecord: values.selectedPaymentRecords,
                },
              },
            },
          },
        },
      };
    }
    if (
      category === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
      values.issueType === GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL
    ) {
      return {
        variables: {
          input: {
            ...requiredVariables,
            issueType: values.issueType,
            linkedTickets: values.selectedRelatedTickets,
            extras: {
              issueType: {
                addIndividualIssueTypeExtras: {
                  household: values.selectedHousehold?.id,
                  individualData: values.individualData,
                },
              },
            },
          },
        },
      };
    }
    if (
      category === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
      values.issueType === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL
    ) {
      return {
        variables: {
          input: {
            ...requiredVariables,
            issueType: values.issueType,
            linkedTickets: values.selectedRelatedTickets,
            extras: {
              issueType: {
                individualDeleteIssueTypeExtras: {
                  individual: values.selectedIndividual?.id,
                },
              },
            },
          },
        },
      };
    }
    if (
      category === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
      values.issueType === GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL
    ) {
      return {
        variables: {
          input: {
            ...requiredVariables,
            issueType: values.issueType,
            linkedTickets: values.selectedRelatedTickets,
            extras: {
              issueType: {
                individualDataUpdateIssueTypeExtras: {
                  individual: values.selectedIndividual?.id,
                  individualData: values.individualDataUpdateFields
                    .filter((item) => item.fieldName)
                    .reduce((prev, current) => {
                      // eslint-disable-next-line no-param-reassign
                      prev[camelCase(current.fieldName)] = current.fieldValue;
                      return prev;
                    }, {}),
                },
              },
            },
          },
        },
      };
    }
    if (
      category === GRIEVANCE_CATEGORIES.DATA_CHANGE &&
      values.issueType === GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD
    ) {
      return {
        variables: {
          input: {
            ...requiredVariables,
            issueType: values.issueType,
            linkedTickets: values.selectedRelatedTickets,
            extras: {
              issueType: {
                householdDataUpdateIssueTypeExtras: {
                  household: values.selectedHousehold?.id,
                  householdData: values.householdDataUpdateFields
                    .filter((item) => item.fieldName)
                    .reduce((prev, current) => {
                      // eslint-disable-next-line no-param-reassign
                      prev[camelCase(current.fieldName)] = current.fieldValue;
                      return prev;
                    }, {}),
                },
              },
            },
          },
        },
      };
    }
    return {
      variables: {
        input: {
          ...requiredVariables,
          linkedTickets: values.selectedRelatedTickets,
        },
      },
    };
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        try {
          await mutate(
            prepareVariables(values.category.toString(), values),
          ).then((res) => {
            return showMessage('Grievance Ticket created.', {
              pathname: `/${businessArea}/grievance-and-feedback/${res.data.createGrievanceTicket.grievanceTickets[0].id}`,
              historyMethod: 'push',
            });
          });
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
      }}
      validationSchema={validationSchema}
    >
      {({ submitForm, values, setFieldValue }) => (
        <>
          <PageHeader
            title={`Edit Ticket #${decodeIdString(id)}`}
            breadCrumbs={breadCrumbsItems}
          />
          <Grid container spacing={3}>
            <Grid item xs={8}>
              <NewTicket>
                <ContainerColumnWithBorder>
                  <Grid container spacing={3}>
                    <Grid item xs={6}>
                      <Field
                        name='category'
                        label='Category*'
                        onChange={(e) => {
                          setFieldValue('category', e.target.value);
                          setFieldValue('issueType', null);
                        }}
                        variant='outlined'
                        choices={
                          choicesData.grievanceTicketManualCategoryChoices
                        }
                        component={FormikSelectField}
                      />
                    </Grid>
                    {values.category.toString() ===
                      GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE ||
                    values.category.toString() ===
                      GRIEVANCE_CATEGORIES.DATA_CHANGE ? (
                      <Grid item xs={6}>
                        <Field
                          name='issueType'
                          label='Issue Type*'
                          variant='outlined'
                          choices={
                            issueTypeDict[values.category.toString()]
                              .subCategories
                          }
                          component={FormikSelectField}
                        />
                      </Grid>
                    ) : null}
                  </Grid>
                  <BoxWithBorders>
                    <Box display='flex' flexDirection='column'>
                      <Consent />
                      <Field
                        name='consent'
                        label='Received Consent*'
                        color='primary'
                        component={FormikCheckboxField}
                      />
                      <LookUpSection
                        category={values.category}
                        values={values}
                        onValueChange={setFieldValue}
                      />
                    </Box>
                  </BoxWithBorders>
                  <BoxWithBorderBottom>
                    <Grid container spacing={3}>
                      <Grid item xs={6}>
                        <Field
                          name='assignedTo'
                          label='Assigned to*'
                          variant='outlined'
                          choices={mappedIndividuals}
                          component={FormikSelectField}
                        />
                      </Grid>
                    </Grid>
                  </BoxWithBorderBottom>
                  <BoxPadding>
                    <Grid container spacing={3}>
                      <Grid item xs={12}>
                        <Field
                          name='description'
                          multiline
                          fullWidth
                          variant='outlined'
                          label='Description*'
                          component={FormikTextField}
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <Field
                          name='admin'
                          label='Administrative Level 2'
                          variant='outlined'
                          component={FormikAdminAreaAutocomplete}
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <Field
                          name='area'
                          fullWidth
                          variant='outlined'
                          label='Area / Village / Pay point'
                          component={FormikTextField}
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <Field
                          name='language'
                          multiline
                          fullWidth
                          variant='outlined'
                          label='Languages Spoken*'
                          component={FormikTextField}
                        />
                      </Grid>
                    </Grid>
                  </BoxPadding>
                  <BoxPadding>
                    {values.category.toString() ===
                      GRIEVANCE_CATEGORIES.DATA_CHANGE &&
                      values.issueType.toString() ===
                        GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL && (
                        <AddIndividualDataChange values={values} />
                      )}
                    {values.category.toString() ===
                      GRIEVANCE_CATEGORIES.DATA_CHANGE &&
                      values.issueType.toString() ===
                        GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL && (
                        <EditIndividualDataChange
                          individual={values.selectedIndividual}
                          values={values}
                          setFieldValue={setFieldValue}
                        />
                      )}
                    {values.category.toString() ===
                      GRIEVANCE_CATEGORIES.DATA_CHANGE &&
                      values.issueType.toString() ===
                        GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD && (
                        <EditHouseholdDataChange
                          household={values.selectedHousehold}
                          values={values}
                          setFieldValue={setFieldValue}
                        />
                      )}
                  </BoxPadding>

                  <DialogFooter>
                    <DialogActions>
                      <Button
                        component={Link}
                        to={`/${businessArea}/grievance-and-feedback`}
                      >
                        Cancel
                      </Button>
                      <Button
                        color='primary'
                        variant='contained'
                        onClick={submitForm}
                      >
                        Save
                      </Button>
                    </DialogActions>
                  </DialogFooter>
                </ContainerColumnWithBorder>
              </NewTicket>
            </Grid>
            <Grid item xs={4}>
              <NewTicket>
                {values.category && values.selectedHousehold?.id ? (
                  <OtherRelatedTicketsCreate values={values} />
                ) : null}
              </NewTicket>
            </Grid>
          </Grid>
        </>
      )}
    </Formik>
  );
}
