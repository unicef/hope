import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { useTargetPopulationLazyQuery } from '@generated/graphql';
import { Grid2 as Grid, Typography } from '@mui/material';
import { FormikCurrencyAutocomplete } from '@shared/Formik/FormikCurrencyAutocomplete';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { tomorrow } from '@utils/utils';
import { Field } from 'formik';
import { ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { CalendarTodayRounded } from '@mui/icons-material';

interface PaymentPlanParametersProps {
  values;
  paymentPlan?;
}

export const PaymentPlanParameters = ({
  values,
  paymentPlan,
}: PaymentPlanParametersProps): ReactElement => {
  const { t } = useTranslation();
  const [loadTargetPopulation, { data, loading }] =
    useTargetPopulationLazyQuery();

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
        <Typography variant="h6">{t('Parameters')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid spacing={3} container>
          <Grid size={{ xs: 4 }}>
            <Field
              name="startDate"
              label={t('Start Date')}
              component={FormikDateField}
              required
              minDate={data?.paymentPlan?.program?.startDate}
              maxDate={values.endDate || data?.paymentPlan?.program?.endDate}
              disabled={!data || loading || Boolean(paymentPlan?.isFollowUp)}
              fullWidth
              decoratorEnd={<CalendarTodayRounded color="disabled" />}
              dataCy="input-start-date"
              tooltip={t(
                'The first day of the period intended to be covered by the payment plan. Note that individuals/households cannot be paid twice from the same programme within this period.',
              )}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <Field
              name="endDate"
              label={t('End Date')}
              component={FormikDateField}
              required
              minDate={values.startDate}
              maxDate={data?.paymentPlan?.program?.endDate}
              disabled={!values.startDate || Boolean(paymentPlan?.isFollowUp)}
              initialFocusedDate={values.startDate}
              fullWidth
              decoratorEnd={<CalendarTodayRounded color="disabled" />}
              dataCy="input-end-date"
              tooltip={t(
                'The last day of the period intended to be covered by the payment plan. Note that individuals/households cannot be paid twice from the same programme within this period.',
              )}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <Field
              name="currency"
              component={FormikCurrencyAutocomplete}
              required
              disabled={Boolean(paymentPlan?.isFollowUp)}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <Field
              name="dispersionStartDate"
              label={t('Dispersion Start Date')}
              component={FormikDateField}
              required
              disabled={!data || loading}
              fullWidth
              decoratorEnd={<CalendarTodayRounded color="disabled" />}
              dataCy="input-dispersion-start-date"
              tooltip={t(
                'The first day from which payments could be delivered.',
              )}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <Field
              name="dispersionEndDate"
              label={t('Dispersion End Date')}
              component={FormikDateField}
              required
              minDate={tomorrow}
              disabled={!values.dispersionStartDate}
              initialFocusedDate={values.dispersionStartDate}
              fullWidth
              decoratorEnd={<CalendarTodayRounded color="disabled" />}
              dataCy="input-dispersion-end-date"
              tooltip={t('The last day on which payments could be delivered.')}
            />
          </Grid>
        </Grid>
      </OverviewContainer>
    </PaperContainer>
  );
};
