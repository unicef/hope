import React from 'react';
import {
  Button,
  TextField,
  Dialog,
  DialogContent,
  Typography,
  FormControl,
  FormLabel,
  FormControlLabel,
  Radio,
  RadioGroup,
} from '@material-ui/core';
import styled from 'styled-components';
import { Formik, Form, Field } from 'formik';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { useProgrammeChoiceDataQuery } from '../../../__generated__/graphql';

const DialogTitle = styled.div`
  padding: 16px;
  margin: 0;
  border-bottom: 1px solid #e4e4e4;
`;

const DialogFooter = styled.div`
  padding: 16px;
  margin: 0;
  border-top: 1px solid #e4e4e4;
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 0 0 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

const MediumLabel = styled.div`
  width: 60%;
  margin: 12px 0;
`;

const DateFields = styled.div`
  display: flex;
`;

export function Programme() {
  const [open, setOpen] = React.useState(false);
  const { data } = useProgrammeChoiceDataQuery();

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const submitForm = (values) => {
    console.log('blah blah submit', values);
  };

  return data ? (
    <div>
      <Button variant='contained' color='primary' onClick={handleClickOpen}>
        new programme
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby='form-dialog-title'
      >
        <DialogTitle>
          <Typography variant='h6'>Set-up a new Programme</Typography>
        </DialogTitle>
        <Formik
          initialValues={{}}
          onSubmit={(values) => {
            return submitForm(values);
          }}
        >
          <Form>
            <DialogContent>
              <DialogDescription>
                To subscribe to this website, please enter your email address
                here. We will send updates occasionally.
              </DialogDescription>

              <Field
                name='programmeName'
                label='Programme Name'
                type='text'
                fullWidth
                required
                component={FormikTextField}
              />

              <MediumLabel>
                <Field
                  name='cashAssisst'
                  label='CashAssist Scope'
                  fullWidth
                  choices={data.programScopeChoices}
                  component={FormikSelectField}
                />
              </MediumLabel>

              <DateFields>
                <Field name='dateFrom'>
                  {({ field, form, meta }) => (
                    <TextField
                      {...field}
                      id='from'
                      label='Start Date'
                      type='date'
                      margin='dense'
                      variant='filled'
                      name='dateFrom'
                      required
                      fullWidth
                      value={form.values.dateFrom}
                      InputLabelProps={{
                        shrink: true,
                      }}
                    />
                  )}
                </Field>

                <Field name='dateTo'>
                  {({ field, form, meta }) => {
                    return (<TextField
                      {...field}
                      id='to'
                      label='End Date'
                      type='date'
                      margin='dense'
                      variant='filled'
                      name='dateTo'
                      required
                      fullWidth
                      value={form.values.dateTo}
                      InputLabelProps={{
                        shrink: true,
                      }}
                    />)
                  }}
                </Field>
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
                  required
                  fullWidth
                  component={FormikTextField}
                />
              </MediumLabel>
              <Field name='frequencyOfPayment'>
                {({ field, form, meta }) => (
                  <FormControl component='fieldset'>
                    <FormLabel component='legend'>
                      Frequency of Payment
                    </FormLabel>
                    <RadioGroup {...field} aria-label='gender' name='gender1'>
                      {data.programFrequencyOfPaymentsChoices.map(
                        (each) => (
                          <FormControlLabel
                            value={each[0]}
                            label={each[1]}
                            control={<Radio />}
                          />
                        ),
                      )}
                    </RadioGroup>
                  </FormControl>
                )}
              </Field>

              <Field
                name='areasOfImplementation'
                label='Administrative Areas of Implementation'
                type='text'
                required
                fullWidth
                component={FormikTextField}
              />
              <MediumLabel>
                <Field
                  name='populationGoal'
                  label='Population goal'
                  type='number'
                  required
                  fullWidth
                  component={FormikTextField}
                />
              </MediumLabel>

              <MediumLabel>
                <Field
                  name='sector'
                  label='Sector'
                  fullWidth
                  choices={data.programSectorChoices}
                  component={FormikSelectField}
                />
              </MediumLabel>
            </DialogContent>

            <DialogFooter>
              <Button onClick={handleClose} color='primary'>
                Cancel
              </Button>
              <Button type='submit' color='primary' variant='contained'>
                Save
              </Button>
            </DialogFooter>
          </Form>
        </Formik>
      </Dialog>
    </div>
  ) : (
    <div> Loading ... </div>
  );
}
