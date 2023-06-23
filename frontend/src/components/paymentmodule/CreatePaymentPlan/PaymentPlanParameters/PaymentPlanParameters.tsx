import { Grid, Typography } from '@material-ui/core';
import { Field } from 'formik';
import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { FormikDateField } from '../../../../shared/Formik/FormikDateField';
import { OverviewContainer } from '../../../core/OverviewContainer';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { Title } from '../../../core/Title';
import { FormikCurrencyAutocomplete } from '../../../../shared/FormikCurrencyAutocomplete';
import { useTargetPopulationLazyQuery } from '../../../../__generated__/graphql';
import { tomorrow } from '../../../../utils/utils';

interface PaymentPlanParametersProps {
  values;
  paymentPlan?;
}

export const PaymentPlanParameters = ({
  values,
  paymentPlan,
}: PaymentPlanParametersProps): React.ReactElement => {
  const { t } = useTranslation();
  const [
    loadTargetPopulation,
    { data, loading },
  ] = useTargetPopulationLazyQuery();

  useEffect(() => {
    if (values.targetingId) {
      loadTargetPopulation({
        variables: {
          id: values.targetingId,
        },
      });
    }
  }, [values.targetingId, loadTargetPopulation]);

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
              minDate={data?.targetPopulation?.program?.startDate}
              maxDate={
                values.endDate || data?.targetPopulation?.program?.endDate
              }
              disabled={!data || loading || Boolean(paymentPlan?.isFollowUp)}
              fullWidth
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
              data-cy='input-start-date'
              tooltip={t(
                'The first day of the period intended to be covered by the payment plan. Note that individuals/households cannot be paid twice from the same programme within this period.',
              )}
            />
          </Grid>
          <Grid item xs={4}>
            <Field
              name='endDate'
              label={t('End Date')}
              component={FormikDateField}
              required
              minDate={values.startDate}
              maxDate={data?.targetPopulation?.program?.endDate}
              disabled={!values.startDate || Boolean(paymentPlan?.isFollowUp)}
              initialFocusedDate={values.startDate}
              fullWidth
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
              data-cy='input-end-date'
              tooltip={t(
                'The last day of the period intended to be covered by the payment plan. Note that individuals/households cannot be paid twice from the same programme within this period.',
              )}
            />
          </Grid>
          <Grid item xs={4}>
            <Field
              name='currency'
              component={FormikCurrencyAutocomplete}
              required
              disabled={Boolean(paymentPlan?.isFollowUp)}
            />
          </Grid>
          <Grid item xs={4}>
            <Field
              name='dispersionStartDate'
              label={t('Dispersion Start Date')}
              component={FormikDateField}
              required
              disabled={!data || loading}
              fullWidth
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
              data-cy='input-dispersion-start-date'
              tooltip={t(
                'The first day from which payments could be delivered.',
              )}
            />
          </Grid>
          <Grid item xs={4}>
            <Field
              name='dispersionEndDate'
              label={t('Dispersion End Date')}
              component={FormikDateField}
              required
              minDate={tomorrow}
              disabled={!values.dispersionStartDate}
              initialFocusedDate={values.dispersionStartDate}
              fullWidth
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
              data-cy='input-dispersion-end-date'
              tooltip={t('The last day on which payments could be delivered.')}
            />
          </Grid>
        </Grid>
      </OverviewContainer>
    </PaperContainer>
  );
};
