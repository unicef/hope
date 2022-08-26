import { Grid, Typography } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { FormikDateField } from '../../../../shared/Formik/FormikDateField';
import { OverviewContainer } from '../../../core/OverviewContainer';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { Title } from '../../../core/Title';
import { CurrencyChoicesQuery } from '../../../../__generated__/graphql';

interface PaymentPlanParametersProps {
  values;
  currencyChoicesData: CurrencyChoicesQuery['currencyChoices'];
}

export const PaymentPlanParameters = ({
  values,
  currencyChoicesData,
}: PaymentPlanParametersProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <PaperContainer>
      <Title>
        <Typography variant='h6'>{t('Parameters')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid spacing={3} container>
          <Grid item xs={4}>
            <Field
              name='startDate'
              label={t('Start Date')}
              component={FormikDateField}
              required
              fullWidth
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
            />
          </Grid>
          <Grid item xs={4}>
            <Field
              name='endDate'
              label={t('End Date')}
              component={FormikDateField}
              required
              minDate={values.startDate}
              disabled={!values.startDate}
              initialFocusedDate={values.startDate}
              fullWidth
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
            />
          </Grid>

          <Grid item xs={4}>
            <Field
              name='currency'
              fullWidth
              variant='outlined'
              label={t('Currency')}
              component={FormikSelectField}
              choices={currencyChoicesData}
              required
            />
          </Grid>
          <Grid item xs={4}>
            <Field
              name='dispersionStartDate'
              label={t('Dispersion Start Date')}
              component={FormikDateField}
              required
              fullWidth
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
            />
          </Grid>
          <Grid item xs={4}>
            <Field
              name='dispersionEndDate'
              label={t('Dispersion End Date')}
              component={FormikDateField}
              required
              minDate={values.dispersionStartDate}
              disabled={!values.dispersionStartDate}
              initialFocusedDate={values.dispersionStartDate}
              fullWidth
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
            />
          </Grid>
        </Grid>
      </OverviewContainer>
    </PaperContainer>
  );
};
