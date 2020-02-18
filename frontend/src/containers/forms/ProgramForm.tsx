import React from 'react';
import * as Yup from 'yup';
import styled from 'styled-components';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field, Form, Formik } from 'formik';
import moment from 'moment';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikSwitchField } from '../../shared/Formik/FormikSwitchField';
import {
  ProgramNode,
  useProgrammeChoiceDataQuery,
} from '../../__generated__/graphql';
import { FormikRadioGroup } from '../../shared/Formik/FormikRadioGroup';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import { selectFields } from '../../utils/utils';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
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

const DialogContainer = styled.div`
  position: absolute;
`;

const validationSchema = Yup.object().shape({
  name: Yup.string().required('Programme name is required'),
  scope: Yup.string().required('CashAssist Scope is required'),
  startDate: Yup.date().required(),
  endDate: Yup.date().when(
    'startDate',
    (startDate, schema) =>
      startDate &&
      schema.min(
        startDate,
        `End date have to be grater than ${moment(startDate).format(
          'DD/MM/YYYY',
        )}`,
      ),
    '',
  ),
  sector: Yup.string().required('Sector is required'),
  budget: Yup.number().min(0),
});

interface ProgramFormPropTypes {
  program?: ProgramNode;
  onSubmit: (values) => Promise<void>;
  renderSubmit: (submit: () => Promise<void>) => void;
  open: boolean;
  onClose: () => void;
  title: string;
}

export function ProgramForm({
  program,
  onSubmit,
  renderSubmit,
  open,
  onClose,
  title,
}: ProgramFormPropTypes): React.ReactElement {
  const { data } = useProgrammeChoiceDataQuery();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let initialValue: { [key: string]: any } = {
    name: '',
    scope: '',
    startDate: '',
    endDate: '',
    description: '',
    budget: '0.00',
    administrativeAreasOfImplementation: '',
    populationGoal: 0,
    frequencyOfPayments: 'REGULAR',
    sector: '',
    cashPlus: false,
  };

  if (program) {
    initialValue = selectFields(program, Object.keys(initialValue));
  }
  if (initialValue.budget === 0) {
    initialValue.budget = '0.00';
  }
  // initialValue.budget =
  if (!data) return null;
  return (
    <DialogContainer>
      <Formik
        initialValues={initialValue}
        onSubmit={(values) => {
          const newValues = { ...values };
          newValues.budget = Number(values.budget).toFixed(2);
          return onSubmit(values);
        }}
        validationSchema={validationSchema}
      >
        {({ submitForm, values }) => (
          <Form>
            <Dialog
              open={open}
              onClose={onClose}
              scroll='paper'
              aria-labelledby='form-dialog-title'
            >
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title' disableTypography>
                  <Typography variant='h6'>{title}</Typography>
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
                      component={FormikDateField}
                      required
                      fullWidth
                      decoratorEnd={
                        <CalendarTodayRoundedIcon color='disabled' />
                      }
                    />
                  </DateField>
                  <DateField>
                    <Field
                      name='endDate'
                      label='End Date'
                      component={FormikDateField}
                      required
                      disabled={!values.startDate}
                      initialFocusedDate={values.startDate}
                      fullWidth
                      decoratorEnd={
                        <CalendarTodayRoundedIcon color='disabled' />
                      }
                      minDate={values.startDate}
                    />
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
                    precision={2}
                    component={FormikTextField}
                  />
                </MediumLabel>
                <Field
                  name='frequencyOfPayments'
                  label='Frequency of Payment'
                  choices={data.programFrequencyOfPaymentsChoices}
                  component={FormikRadioGroup}
                />
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
                  />
                </MediumLabel>
              </DialogContent>
              {renderSubmit(submitForm)}
            </Dialog>
          </Form>
        )}
      </Formik>
    </DialogContainer>
  );
}
