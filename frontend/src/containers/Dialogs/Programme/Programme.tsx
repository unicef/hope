import React, { useState } from 'react';
import moment from 'moment';
import * as Yup from 'yup';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import {
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  FormControl,
  FormLabel,
  FormControlLabel,
  Radio,
  RadioGroup,
} from '@material-ui/core';
import { Formik, Form, Field } from 'formik';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { FormikSwitchField } from '../../../shared/Formik/FormikSwitchField';
import {
  useProgrammeChoiceDataQuery,
  useCreateProgramMutation,
} from '../../../__generated__/graphql';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid #e4e4e4;
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid #e4e4e4;
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

const MediumLabel = styled.div`
  width: 60%;
  margin: 12px 0;
`;

const DateFields = styled.div`
  display: flex;
  justify-content: space-between;
  margin: 12px 0;
`;

const DateField = styled.div`
  width: 48%;
`;

const validationSchema = Yup.object().shape({
  name: Yup.string().required('Programme name is required'),
  scope: Yup.string().required('CashAssist Scope is required'),
  startDate: Yup.string().required('Start Date is required'),
  endDate: Yup.string().required('End Date is required'),
  sector: Yup.string().required('Sector is required'),
});

export function Programme(): React.ReactElement {
  const history = useHistory();
  const [open, setOpen] = useState(false);
  const [toggle, setToggle] = useState(false);
  const { data } = useProgrammeChoiceDataQuery();
  const [mutate] = useCreateProgramMutation();

  const handleToggle = () => {
    return toggle ? setToggle(false) : setToggle(true);
  };

  const submitFormHandler = async (values) => {
    const response = await mutate({
      variables: {
        programData: {
          ...values,
          startDate: moment(values.startDate).toISOString(),
          endDate: moment(values.endDate).toISOString(),
          locationId:
            'TG9jYXRpb246MzkyZmI5NDYtM2U4Ni0xMWVhLWI3N2YtMmU3MjhjZTg4MTI1',
        },
      },
    });
    if (!response.errors && response.data.createProgram) {
      history.push(`/programs/${response.data.createProgram.program.id}`);
    }
  };
  if (!data) {
    return (
      <Button variant='contained' color='primary' disabled>
        new programme
      </Button>
    );
  }
  return (
    <div>
      <Button variant='contained' color='primary' onClick={() => setOpen(true)}>
        new programme
      </Button>
      <Formik
        initialValues={{
          name: '',
          scope: '',
          startDate: '',
          endDate: '',
          description: '',
          budget: 0,
          administrativeAreasOfImplementation: '',
          populationGoal: 0,
          sector: '',
          cashPlus: false,
        }}
        onSubmit={(values) => {
          return submitFormHandler(values);
        }}
        validationSchema={validationSchema}
      >
        {({ submitForm }) => (
          <Form>
            <Dialog
              open={open}
              onClose={() => setOpen(false)}
              scroll='paper'
              aria-labelledby='form-dialog-title'
            >
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title'>
                  <Typography variant='h6'>Set-up a new Programme</Typography>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogDescription>
                  To subscribe to this website, please enter your email address
                  here. We will send updates occasionally.
                </DialogDescription>

                <Field
                  name='name'
                  label='Programme Name'
                  type='text'
                  fullWidth
                  required
                  component={FormikTextField}
                />

                <MediumLabel>
                  <Field
                    name='scope'
                    label='CashAssist Scope'
                    fullWidth
                    required
                    choices={data.programScopeChoices}
                    component={FormikSelectField}
                  />
                </MediumLabel>
                <DateFields>
                  <DateField>
                    <Field
                      name='startDate'
                      label='Start Date'
                      required
                      fullWidth
                      component={FormikTextField}
                      type='date'
                      InputLabelProps={{
                        shrink: true,
                      }}
                    />
                  </DateField>
                  <DateField>
                    <Field name='endDate'>
                      {({ field, form, meta }) => {
                        return (
                          <TextField
                            {...field}
                            id='to'
                            label='End Date'
                            type='date'
                            margin='dense'
                            variant='filled'
                            name='endDate'
                            required
                            fullWidth
                            disabled={!form.values.startDate}
                            value={form.values.endDate}
                            InputLabelProps={{
                              shrink: true,
                            }}
                            inputProps={{
                              min: form.values.startDate,
                            }}
                          />
                        );
                      }}
                    </Field>
                  </DateField>
                </DateFields>
                <Field
                  name='description'
                  label='Description'
                  type='text'
                  fullWidth
                  component={FormikTextField}
                />
                <MediumLabel>
                  <Field
                    name='budget'
                    label='Budget'
                    type='number'
                    fullWidth
                    component={FormikTextField}
                  />
                </MediumLabel>
                <Field name='frequencyOfPayment'>
                  {({ field }) => (
                    <FormControl component='fieldset'>
                      <FormLabel component='legend'>
                        Frequency of Payment
                      </FormLabel>
                      <RadioGroup
                        {...field}
                        aria-label='gender'
                        name='frequencyOfPayments'
                      >
                        {data.programFrequencyOfPaymentsChoices.map((each) => (
                          <FormControlLabel
                            key={each.value}
                            value={each.value}
                            label={each.name}
                            control={<Radio />}
                          />
                        ))}
                      </RadioGroup>
                    </FormControl>
                  )}
                </Field>
                <Field
                  name='administrativeAreasOfImplementation'
                  label='Administrative Areas of Implementation'
                  type='text'
                  fullWidth
                  component={FormikTextField}
                />
                <MediumLabel>
                  <Field
                    name='populationGoal'
                    label='Population goal'
                    type='number'
                    fullWidth
                    component={FormikTextField}
                  />
                </MediumLabel>
                <MediumLabel>
                  <Field
                    name='sector'
                    label='Sector'
                    fullWidth
                    required
                    choices={data.programSectorChoices}
                    component={FormikSelectField}
                  />
                </MediumLabel>
                <MediumLabel>
                  <Field
                    name='cashPlus'
                    label='Cash+'
                    color='primary'
                    component={FormikSwitchField}
                    checked={toggle}
                    onChange={handleToggle}
                  />
                </MediumLabel>
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={() => setOpen(false)} color='primary'>
                    Cancel
                  </Button>
                  <Button
                    onClick={submitForm}
                    type='submit'
                    color='primary'
                    variant='contained'
                  >
                    Save
                  </Button>
                </DialogActions>
              </DialogFooter>
            </Dialog>
          </Form>
        )}
      </Formik>
    </div>
  );
}
