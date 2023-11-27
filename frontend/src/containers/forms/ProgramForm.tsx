import { Grid } from '@material-ui/core';
import { camelCase } from 'lodash';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field, Form } from 'formik';
import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  useDataCollectionTypeChoiceDataQuery,
  useProgrammeChoiceDataQuery,
} from '../../__generated__/graphql';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import { FormikRadioGroup } from '../../shared/Formik/FormikRadioGroup';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { today } from '../../utils/utils';

interface ProgramFormPropTypes {
  values;
}

export const ProgramForm = ({ values }: ProgramFormPropTypes): ReactElement => {
  const { t } = useTranslation();
  const { data } = useProgrammeChoiceDataQuery();
  const {
    data: dataCollectionTypeChoicesData,
  } = useDataCollectionTypeChoiceDataQuery();

  if (!data || !dataCollectionTypeChoicesData) return null;

  //TODO: Add descriptions to dataCollectionTypeChoicesData (backend)
  const descriptions = {
    full:
      'Full individual collected This type indicates that data has been collected for all of the household members. [Individuals with details collected = size of household].',
    partial:
      'Partial individuals collected This type indicates that data has been collected for the Head of Household, collector, and at least one other individual. However, data collection has not covered every member of the household. [Individuals with details collected < size of household].',
    sizeOnly:
      'Size only collected This type is assigned when only the size of the household (count of individuals) has been collected without collecting specific details about the household members.',
    sizeAgeGenderDisaggregated:
      'No individual data This type is assigned when no data has been collected for any individual other than the head of the household.',
  };

  const filteredDataCollectionTypeChoicesData = dataCollectionTypeChoicesData?.dataCollectionTypeChoices
    .filter((el) => el.name !== '')
    .map((el) => {
      const camelCaseValue = camelCase(el.value);
      return {
        ...el,
        description: descriptions[camelCaseValue],
      };
    });

  return (
    <Form>
      <Grid container spacing={3}>
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
        <Grid item xs={6} />
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
        <Grid item xs={6} />
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
        <Grid item xs={6} />
        <Grid item xs={12}>
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
        <Grid item xs={6} />
        <Grid item xs={12}>
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
        <Grid item xs={6} />
        <Grid item xs={6}>
          <Field
            name='cashPlus'
            label={t('Cash+')}
            color='primary'
            component={FormikCheckboxField}
            data-cy='input-cash-plus'
          />
        </Grid>
        <Grid item xs={6} />
        <Grid item xs={6}>
          <Field
            name='frequencyOfPayments'
            label={t('Frequency of Payment')}
            choices={data.programFrequencyOfPaymentsChoices}
            component={FormikRadioGroup}
            data-cy='input-frequency-of-payment'
            alignItems='center'
          />
        </Grid>
      </Grid>
    </Form>
  );
};
