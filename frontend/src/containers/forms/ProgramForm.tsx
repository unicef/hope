import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field, Form, Formik } from 'formik';
import moment from 'moment';
import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import {
  ProgramQuery,
  useDataCollectionTypeChoiceDataQuery,
  useProgrammeChoiceDataQuery,
} from '../../__generated__/graphql';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import { FormikRadioGroup } from '../../shared/Formik/FormikRadioGroup';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { selectFields, today } from '../../utils/utils';
import { Box, Grid } from '@material-ui/core';

interface ProgramFormPropTypes {
  program?: ProgramQuery['program'];
  onSubmit: (values, setFieldError) => Promise<void>;
  initialValues?: { [key: string]: string | boolean | number };
  actions: (handleSubmit) => ReactElement;
}

export const ProgramForm = ({
  program = null,
  onSubmit,
  initialValues,
  actions,
}: ProgramFormPropTypes): ReactElement => {
  const { t } = useTranslation();
  const { data } = useProgrammeChoiceDataQuery();
  const {
    data: dataCollectionTypeChoicesData,
  } = useDataCollectionTypeChoiceDataQuery();
  const validationSchema = Yup.object().shape({
    name: Yup.string()
      .required(t('Programme name is required'))
      .min(2, t('Too short'))
      .max(150, t('Too long')),
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
    dataCollectingTypeCode: Yup.string().required(
      t('Data Collecting Type is required'),
    ),
  });

  let formInitialValue: {
    [key: string]: string | boolean | number;
  } = initialValues || {
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
    dataCollectingTypeCode: '',
  };

  if (program) {
    formInitialValue = selectFields(program, Object.keys(formInitialValue));
    formInitialValue.individualDataNeeded = program.individualDataNeeded
      ? 'YES'
      : 'NO';
  }
  if (formInitialValue.budget === 0) {
    formInitialValue.budget = '0.00';
  }
  formInitialValue.dataCollectingTypeCode = program?.dataCollectingType?.code;

  if (!data || !dataCollectionTypeChoicesData) return null;

  const withoutIndividualDataText = t(
    'This programme will use only household and/or head of household details for targeting or entitlement calculation',
  );

  const withIndividualDataText = t(
    'This programme will use household member individuals’ details for targeting or entitlement calculation. Setting this flag can reduce the number of households filtered in the target population.',
  );

  const filteredDataCollectionTypeChoicesData = dataCollectionTypeChoicesData?.dataCollectionTypeChoices.filter(
    (el) => el.name !== '',
  );

  return (
    <Formik
      initialValues={formInitialValue}
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
        <Grid container>
          <Form>
            <Grid item xs={6}>
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
            </Grid>
            <Grid item xs={6}>
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
            </Grid>
            <Grid item xs={6}>
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
            </Grid>
            <Grid item xs={6}>
              <Field
                name='dataCollectingTypeCode'
                label={t('Data Collecting Type')}
                fullWidth
                variant='outlined'
                required
                choices={filteredDataCollectionTypeChoicesData || []}
                component={FormikSelectField}
                data-cy='input-data-collecting-type'
              />
            </Grid>
            <Grid item xs={6}>
              <Field
                name='startDate'
                label={t('Start Date')}
                component={FormikDateField}
                required
                fullWidth
                decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
                data-cy='input-start-date'
              />
            </Grid>
            <Grid item xs={6}>
              <Field
                name='endDate'
                label={t('End Date')}
                component={FormikDateField}
                required
                disabled={!values.startDate}
                initialFocusedDate={values.startDate}
                fullWidth
                decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
                minDate={today}
                data-cy='input-end-date'
              />
            </Grid>

            <Grid item xs={6}>
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
            </Grid>
            <Grid item xs={6}>
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
            </Grid>
            <Grid item xs={6}>
              <Field
                name='frequencyOfPayments'
                label={t('Frequency of Payment')}
                choices={data.programFrequencyOfPaymentsChoices}
                component={FormikRadioGroup}
                data-cy='input-frequency-of-payment'
              />
            </Grid>
            <Grid item xs={6}>
              <Field
                name='administrativeAreasOfImplementation'
                label={t('Administrative Areas of Implementation')}
                type='text'
                fullWidth
                variant='outlined'
                component={FormikTextField}
                data-cy='input-admin-area'
              />
            </Grid>
            <Grid item xs={6}>
              <Field
                name='populationGoal'
                label={t('Population Goal (# of Individuals)')}
                type='number'
                fullWidth
                variant='outlined'
                component={FormikTextField}
                data-cy='input-population-goal'
              />
            </Grid>
            <Grid item xs={6}>
              <Field
                name='cashPlus'
                label={t('Cash+')}
                color='primary'
                component={FormikCheckboxField}
                data-cy='input-cash-plus'
              />
            </Grid>
            <Grid item xs={6}>
              <Field
                name='individualDataNeeded'
                disabled={program && program.status === 'ACTIVE'}
                label={t('Data for targeting or entitlement calculation*')}
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
            </Grid>
            <Grid item xs={12}>
              <Box display='flex' justifyContent='space-between'>
                {actions(submitForm)}
              </Box>
            </Grid>
          </Form>
        </Grid>
      )}
    </Formik>
  );
};
