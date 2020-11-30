import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import { Field, Formik } from 'formik';
import { Box, Button, DialogActions, Grid } from '@material-ui/core';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { PageHeader } from '../PageHeader';
import { BreadCrumbsItem } from '../BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';
import {
  useAllAddIndividualFieldsQuery,
  useAllUsersQuery,
  useCreateGrievanceMutation,
  useGrievancesChoiceDataQuery,
} from '../../__generated__/graphql';
import { LoadingComponent } from '../LoadingComponent';
import { useSnackbar } from '../../hooks/useSnackBar';
import { FormikAdminAreaAutocomplete } from '../../shared/Formik/FormikAdminAreaAutocomplete';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
} from '../../utils/constants';
import { Consent } from './Consent';
import { LookUpSection } from './LookUpSection';
import { OtherRelatedTicketsCreate } from './OtherRelatedTicketsCreate';
import { AddIndividualDataChange } from './AddIndividualDataChange';
import { EditIndividualDataChange } from './EditIndividualDataChange';
import { EditHouseholdDataChange } from './EditHouseholdDataChange';
import { TicketsAlreadyExist } from './TicketsAlreadyExist';
import { prepareVariables, validate } from './utils/createGrievanceUtils';
import { useArrayToDict } from '../../hooks/useArrayToDict';
import {renderUserName, thingForSpecificGrievanceType} from '../../utils/utils';

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
const EmptyComponent = (): React.ReactElement => null;
export const dataChangeComponentDict = {
  [GRIEVANCE_CATEGORIES.DATA_CHANGE]: {
    [GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL]: AddIndividualDataChange,
    [GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL]: EditIndividualDataChange,
    [GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD]: EditHouseholdDataChange,
  },
};

const validationSchema = Yup.object().shape({
  description: Yup.string().required('Description is required'),
  assignedTo: Yup.string().required('Assigned To is required'),
  category: Yup.string().required('Category is required').nullable(),
  admin: Yup.string(),
  area: Yup.string(),
  language: Yup.string().required('Language is required'),
  consent: Yup.bool().oneOf([true], 'Consent is required'),
  selectedPaymentRecords: Yup.array().of(Yup.string()).nullable(),
  selectedRelatedTickets: Yup.array().of(Yup.string()).nullable(),
});

export function CreateGrievancePage(): React.ReactElement {
  const businessArea = useBusinessArea();
  const { showMessage } = useSnackbar();

  const initialValues = {
    description: '',
    assignedTo: '',
    category: null,
    language: '',
    consent: false,
    admin: '',
    area: '',
    selectedHousehold: null,
    selectedIndividual: null,
    selectedPaymentRecords: [],
    selectedRelatedTickets: [],
    identityVerified: false,
    issueType: null,
    givenName: '',
    middleName: '',
    familyName: '',
    sex: '',
    birthDate: '',
  };
  const { data: userData, loading: userDataLoading } = useAllUsersQuery({
    variables: { businessArea },
  });

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();

  const [mutate] = useCreateGrievanceMutation();
  const {
    data: allAddIndividualFieldsData,
    loading: allAddIndividualFieldsDataLoading,
  } = useAllAddIndividualFieldsQuery();
  const issueTypeDict = useArrayToDict(
    choicesData?.grievanceTicketIssueTypeChoices,
    'category',
    '*',
  );
  if (
    userDataLoading ||
    choicesLoading ||
    allAddIndividualFieldsDataLoading ||
    !issueTypeDict
  ) {
    return <LoadingComponent />;
  }
  if (!choicesData || !userData) return null;

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

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        try {
          const response = await mutate(prepareVariables(businessArea, values));
          showMessage('Grievance Ticket created.', {
            pathname: `/${businessArea}/grievance-and-feedback/${response.data.createGrievanceTicket.grievanceTickets[0].id}`,
            historyMethod: 'push',
          });
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
      }}
      validate={(values) => validate(values, allAddIndividualFieldsData)}
      validationSchema={validationSchema}
    >
      {({ submitForm, values, setFieldValue }) => {
        const DatachangeComponent = thingForSpecificGrievanceType(
          values,
          dataChangeComponentDict,
          EmptyComponent,
        );
        return (
          <>
            <PageHeader title='New Ticket' breadCrumbs={breadCrumbsItems} />
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
                      {values.category ===
                        GRIEVANCE_CATEGORIES.SENSITIVE_GRIEVANCE ||
                      values.category === GRIEVANCE_CATEGORIES.DATA_CHANGE ? (
                        <Grid item xs={6}>
                          <Field
                            name='issueType'
                            label='Issue Type*'
                            variant='outlined'
                            choices={
                              issueTypeDict[values.category].subCategories
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
                      <DatachangeComponent
                        values={values}
                        setFieldValue={setFieldValue}
                      />
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
                  {values.category &&
                  values.issueType &&
                  values.selectedHousehold?.id &&
                  values.selectedIndividual?.id ? (
                    <TicketsAlreadyExist values={values} />
                  ) : null}
                </NewTicket>
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
}
