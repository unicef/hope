import React from 'react';
import {
  Button,
  TextField,
  Dialog,
  DialogContent,
  Typography,
  FormControl,
  MenuItem,
  InputLabel,
  Select,
  FormLabel,
  FormControlLabel,
  Radio,
  RadioGroup,
} from '@material-ui/core';
import styled from 'styled-components';
import { Formik, Form, Field } from 'formik';
import {
  useFrequencyOfPaymentsQuery,
  useProgramScopeChoicesQuery,
  useProgramSectorChoicesQuery,
} from '../../../__generated__/graphql';

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
  const programFrequencyOfPaymentsChoices = useFrequencyOfPaymentsQuery();
  const programSectorChoices = useProgramSectorChoicesQuery();
  const programScopeChoices = useProgramScopeChoicesQuery();

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const submitForm = (values) => {
    // eslint-disable-next-line
    debugger;
    console.error('blah blah submit', values);
  };

  return (
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
            // eslint-disable-next-line
            debugger;
            return submitForm(values);
          }}
        >
          <Form>
            <DialogContent>
              <DialogDescription>
                To subscribe to this website, please enter your email address
                here. We will send updates occasionally.
              </DialogDescription>

              <Field name='programmeName'>
                {({ field, form, meta }) => (
                  <TextField
                    {...field}
                    autoFocus
                    margin='dense'
                    id='name'
                    label='Programme Name'
                    type='text'
                    variant='filled'
                    name='programmeName'
                    fullWidth
                    required
                  />
                )}
              </Field>

              <Field name='cashAssist'>
                {({ field, form, meta }) => (
                  <MediumLabel>
                    <FormControl variant='filled' margin='dense' fullWidth>
                      <InputLabel>CashAssist Scope</InputLabel>
                      <Select {...field} name='cashAssist'>
                        <MenuItem value=''>
                          <em>None</em>
                        </MenuItem>
                        {programScopeChoices.data.programScopeChoices.map(
                          (each) => (
                            <MenuItem value={each[0]}>{each[1]}</MenuItem>
                          ),
                        )}
                      </Select>
                    </FormControl>
                  </MediumLabel>
                )}
              </Field>

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
                  {({ field, form, meta }) => (
                    <TextField
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
                    />
                  )}
                </Field>
              </DateFields>

              <Field name='description'>
                {({ field, form, meta }) => (
                  <TextField
                    {...field}
                    autoFocus
                    margin='dense'
                    id='description'
                    label='Description'
                    type='text'
                    variant='filled'
                    fullWidth
                  />
                )}
              </Field>
              <Field name='budget'>
                {({ field, form, meta }) => (
                  <MediumLabel>
                    <TextField
                      {...field}
                      autoFocus
                      margin='dense'
                      id='name'
                      label='Budget'
                      type='number'
                      variant='filled'
                      fullWidth
                    />
                  </MediumLabel>
                )}
              </Field>

              <Field name='frequencyOfPayment'>
                {({ field, form, meta }) => (
                  <FormControl component='fieldset'>
                    <FormLabel component='legend'>
                      Frequency of Payment
                    </FormLabel>
                    <RadioGroup {...field} aria-label='gender' name='gender1'>
                      {programFrequencyOfPaymentsChoices.data.programFrequencyOfPaymentsChoices.map(
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

              <Field name='areasOfImplementation'>
                {({ field, form, meta }) => (
                  <TextField
                    {...field}
                    autoFocus
                    margin='dense'
                    id='areas'
                    label='Administrative Areas of Implementation'
                    type='text'
                    variant='filled'
                    fullWidth
                  />
                )}
              </Field>
              <Field name='populationGoal'>
                {({ field, form, meta }) => (
                  <MediumLabel>
                    <TextField
                      {...field}
                      autoFocus
                      margin='dense'
                      id='name'
                      label='Population goal'
                      type='number'
                      variant='filled'
                      fullWidth
                    />
                  </MediumLabel>
                )}
              </Field>
              <Field name='sector'>
                {({ field, form, meta }) => (
                  <MediumLabel>
                    <FormControl variant='filled' margin='dense' fullWidth>
                      <InputLabel>Sector</InputLabel>
                      <Select {...field} name='sector'>
                        <MenuItem value=''>
                          <em>None</em>
                        </MenuItem>
                        {programSectorChoices.data.programSectorChoices.map(each => (
                          <MenuItem value={each[0]}>{each[1]}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </MediumLabel>
                )}
              </Field>
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
  );
}
