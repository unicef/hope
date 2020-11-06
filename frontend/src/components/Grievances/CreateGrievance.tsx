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
import { Consent } from './Consent';
import { LookUpSection } from './LookUpSection';
import {
  useAllIndividualsQuery,
  useCreateGrievanceTicketMutation,
  useGrievancesChoiceDataQuery,
} from '../../__generated__/graphql';
import { LoadingComponent } from '../LoadingComponent';
import { useSnackbar } from '../../hooks/useSnackBar';
import { AdminAreasAutocomplete } from '../population/AdminAreaAutocomplete';

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

export function CreateGrievance(): React.ReactElement {
  const businessArea = useBusinessArea();
  const { showMessage } = useSnackbar();

  const initialValues = {
    description: '',
    assignedTo: '',
    category: null,
    language: '',
    consent: false,
    selectedHousehold: '',
    selectedIndividual: '',
    selectedPaymentRecords: [],
    selectedRelatedTickets: [],
    identityVerified: false,
  };

  const validationSchema = Yup.object().shape({
    description: Yup.string().required('Description is required'),
    assignedTo: Yup.string().required('Assigned To is required'),
    category: Yup.string()
      .required('Category is required')
      .nullable(),
    language: Yup.string().required('Language is required'),
    consent: Yup.bool().oneOf([true], 'Consent is required'),
    // selectedHousehold: Yup.string().required('Household has to be selected'),
    // selectedIndividual: Yup.string().required('Individual has to be selected'),
    // selectedPaymentRecords: Yup.array.of(Yup.string()),
    // selectedRelatedTickets: Yup.array.of(Yup.string()),
  });

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Grievance and Feedback',
      to: `/${businessArea}/grievance-and-feedback/`,
    },
  ];
  const {
    data: individualsData,
    loading: individualsDataLoading,
  } = useAllIndividualsQuery({
    variables: {
      first: 20,
    },
  });

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();
  const [mutate] = useCreateGrievanceTicketMutation();

  if (!choicesData || !individualsData) return null;
  if (individualsDataLoading || choicesLoading) {
    return <LoadingComponent />;
  }

  const mappedIndividuals = individualsData.allIndividuals.edges.map(
    (edge) => ({
      name: edge.node.fullName,
      value: edge.node.id,
    }),
  );

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        mutate({
          variables: {
            input: {
              businessArea,
              description: values.description,
              assignedTo: values.assignedTo,
              category: parseInt(values.category, 10),
              consent: values.consent,
              language: values.language,
            },
          },
        }).then(
          (res) => {
            return showMessage('Grievance Ticket created.', {
              pathname: `/${businessArea}/grievance-and-feedback/${res.data.createGrievanceTicket.grievanceTickets[0].id}`,
              historyMethod: 'push',
            });
          },
          () => {
            return showMessage('Something went wrong.');
          },
        );
      }}
      validationSchema={validationSchema}
    >
      {({ submitForm, values, setFieldValue }) => (
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
                        variant='outlined'
                        choices={choicesData.grievanceTicketCategoryChoices}
                        component={FormikSelectField}
                      />
                    </Grid>
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
                          component={AdminAreasAutocomplete}
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
                          label='Languages Spoken'
                          component={FormikTextField}
                        />
                      </Grid>
                    </Grid>
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
          </Grid>
        </>
      )}
    </Formik>
  );
}
