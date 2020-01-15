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
} from '@material-ui/core';
import styled from 'styled-components';
import { Formik, Form, Field } from 'formik';

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

export function Programme() {
  const [open, setOpen] = React.useState(false);

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
                        <MenuItem value={10}>Ten</MenuItem>
                        <MenuItem value={20}>Twenty</MenuItem>
                        <MenuItem value={30}>Thirty</MenuItem>
                      </Select>
                    </FormControl>
                  </MediumLabel>
                )}
              </Field>

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
                  <MediumLabel>
                    <FormControl variant='filled' margin='dense' fullWidth>
                      <InputLabel>Frequency of Payment</InputLabel>
                      <Select {...field} name='frequencyOfPayment'>
                        <MenuItem value=''>
                          <em>None</em>
                        </MenuItem>
                        <MenuItem value={10}>Ten</MenuItem>
                        <MenuItem value={20}>Twenty</MenuItem>
                        <MenuItem value={30}>Thirty</MenuItem>
                      </Select>
                    </FormControl>
                  </MediumLabel>
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
                        <MenuItem value={10}>Ten</MenuItem>
                        <MenuItem value={20}>Twenty</MenuItem>
                        <MenuItem value={30}>Thirty</MenuItem>
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
