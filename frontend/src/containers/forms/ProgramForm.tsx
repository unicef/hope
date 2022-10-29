import {
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field, Form, Formik } from 'formik';
import moment from 'moment';
import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import * as Yup from 'yup';
import { AutoSubmitFormOnEnter } from '../../components/core/AutoSubmitFormOnEnter';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import { FormikRadioGroup } from '../../shared/Formik/FormikRadioGroup';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { selectFields } from '../../utils/utils';
import {
  ProgramNode,
  useProgrammeChoiceDataQuery,
} from '../../__generated__/graphql';
import { DialogActions } from '../dialogs/DialogActions';
import { DialogDescription } from '../dialogs/DialogDescription';
import { DialogFooter } from '../dialogs/DialogFooter';
import { DialogTitleWrapper } from '../dialogs/DialogTitleWrapper';

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
const FullWidth = styled.div`
  width: 100%;
`;

const today = new Date();
today.setHours(0, 0, 0, 0);

interface ProgramFormPropTypes {
  program?: ProgramNode;
  onSubmit: (values, setFieldError) => Promise<void>;
  renderSubmit: (submit: () => Promise<void>) => ReactElement;
  open: boolean;
  onClose: () => void;
  title: string;
}

export const ProgramForm = ({
  program = null,
  onSubmit,
  renderSubmit,
  open,
  onClose,
  title,
}: ProgramFormPropTypes): ReactElement => {
  const { t } = useTranslation();
  const { data } = useProgrammeChoiceDataQuery();

  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .required(t('Programme name is required'))
      .min(2, t('Too short'))
      .max(255, t('Too long')),
    scope: Yup.string()
      .required(t('CashAssist Scope is required'))
      .min(2, t('Too short'))
      .max(50, t('Too long')),
    startDate: Yup.date().required(t('Start Date is required')),
    endDate: Yup.date()
      .required(t('End Date is required'))
      .min(today, t('End Date cannot be in the past'))
      .when(
        'startDate',
        (startDate, schema) =>
          startDate &&
          schema.min(
            startDate,
            `${t('End date have to be greater than')} ${moment(
              startDate,
            ).format('YYYY-MM-DD')}`,
          ),
        '',
      ),
    sector: Yup.string()
      .required(t('Sector is required'))
      .min(2, t('Too short'))
      .max(50, t('Too long')),
    budget: Yup.number()
      .min(0)
      .max(99999999, t('Number is too big')),
    administrativeAreasOfImplementation: Yup.string()
      .min(2, t('Too short'))
      .max(255, t('Too long')),
    description: Yup.string()
      .min(2, t('Too short'))
      .max(255, t('Too long')),
    populationGoal: Yup.number()
      .min(0)
      .max(99999999, t('Number is too big')),
  });

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
    individualDataNeeded: 'NO',
  };
  if (program) {
    initialValue = selectFields(program, Object.keys(initialValue));
    initialValue.individualDataNeeded = program.individualDataNeeded
      ? 'YES'
      : 'NO';
  }
  if (initialValue.budget === 0) {
    initialValue.budget = '0.00';
  }
  if (!data) return null;

  const withoutIndividualDataText = t(
    'This programme will use only household and/or head of household details for targeting or entitlement calculation',
  );

  const withIndividualDataText = t(
    'This programme will use household member individuals’ details for targeting or entitlement calculation. Setting this flag can reduce the number of households filtered in the target population.',
  );

  return (
    <DialogContainer>
      <Dialog
        open={open}
        onClose={onClose}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <Formik
          initialValues={initialValue}
          onSubmit={(values, { setFieldError }) => {
            const newValues = { ...values };
            newValues.budget = Number(values.budget).toFixed(2);
            if (values.individualDataNeeded === 'YES') {
              newValues.individualDataNeeded = true;
            } else if (values.individualDataNeeded === 'NO') {
              newValues.individualDataNeeded = false;
            }
            return onSubmit(newValues, setFieldError);
          }}
          validationSchema={validationSchema}
          enableReinitialize
        >
          {({ submitForm, values }) => (
            <>
              {open && <AutoSubmitFormOnEnter />}
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title' disableTypography>
                  <Typography variant='h6'>{title}</Typography>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogDescription>
                  {t(
                    'To create a new Programme, please complete all required fields on the form below and save.',
                  )}
                </DialogDescription>
                <Form>
                  <Field
                    name='name'
                    label={t('Programme Name')}
                    type='text'
                    fullWidth
                    required
                    variant='outlined'
                    component={FormikTextField}
                    data-cy='input-programme-name'
                  />
                  <Field
                    name='scope'
                    label={t('CashAssist Scope')}
                    fullWidth
                    variant='outlined'
                    required
                    choices={data.programScopeChoices}
                    component={FormikSelectField}
                    data-cy='input-cash-assist-scope'
                  />
                  <Field
                    name='sector'
                    label={t('Sector')}
                    fullWidth
                    required
                    variant='outlined'
                    choices={data.programSectorChoices}
                    component={FormikSelectField}
                    data-cy='input-sector'
                  />
                  <DateFields>
                    <DateField>
                      <Field
                        name='startDate'
                        label={t('Start Date')}
                        component={FormikDateField}
                        required
                        fullWidth
                        decoratorEnd={
                          <CalendarTodayRoundedIcon color='disabled' />
                        }
                        data-cy='input-start-date'
                      />
                    </DateField>
                    <DateField>
                      <Field
                        name='endDate'
                        label={t('End Date')}
                        component={FormikDateField}
                        required
                        disabled={!values.startDate}
                        initialFocusedDate={values.startDate}
                        fullWidth
                        decoratorEnd={
                          <CalendarTodayRoundedIcon color='disabled' />
                        }
                        minDate={today}
                        data-cy='input-end-date'
                      />
                    </DateField>
                  </DateFields>
                  <Field
                    name='description'
                    label={t('Description')}
                    type='text'
                    fullWidth
                    multiline
                    variant='outlined'
                    component={FormikTextField}
                    data-cy='input-description'
                  />
                  <Field
                    name='budget'
                    label={t('Budget (USD)')}
                    type='number'
                    fullWidth
                    precision={2}
                    variant='outlined'
                    component={FormikTextField}
                    data-cy='input-budget'
                  />
                  <Field
                    name='frequencyOfPayments'
                    label={t('Frequency of Payment')}
                    choices={data.programFrequencyOfPaymentsChoices}
                    component={FormikRadioGroup}
                    data-cy='input-frequency-of-payment'
                  />
                  <Field
                    name='administrativeAreasOfImplementation'
                    label={t('Administrative Areas of Implementation')}
                    type='text'
                    fullWidth
                    variant='outlined'
                    component={FormikTextField}
                    data-cy='input-admin-area'
                  />
                  <Field
                    name='populationGoal'
                    label={t('Population Goal (# of Individuals)')}
                    type='number'
                    fullWidth
                    variant='outlined'
                    component={FormikTextField}
                    data-cy='input-population-goal'
                  />
                  <FullWidth>
                    <Field
                      name='cashPlus'
                      label={t('Cash+')}
                      color='primary'
                      component={FormikCheckboxField}
                      data-cy='input-cash-plus'
                    />
                  </FullWidth>
                  <FullWidth>
                    <Field
                      name='individualDataNeeded'
                      disabled={program && program.status === 'ACTIVE'}
                      label={t(
                        'Data for targeting or entitlement calculation*',
                      )}
                      choices={[
                        {
                          name: withoutIndividualDataText,
                          value: 'NO',
                        },
                        {
                          name: withIndividualDataText,
                          value: 'YES',
                        },
                      ]}
                      component={FormikRadioGroup}
                      data-cy='input-individual-data-needed'
                    />
                  </FullWidth>
                </Form>
              </DialogContent>
              <DialogFooter>
                <DialogActions>{renderSubmit(submitForm)}</DialogActions>
              </DialogFooter>
            </>
          )}
        </Formik>
      </Dialog>
    </DialogContainer>
  );
};
