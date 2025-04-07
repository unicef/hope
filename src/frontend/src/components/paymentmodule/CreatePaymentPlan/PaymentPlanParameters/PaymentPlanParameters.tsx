import { Title } from '@core/Title';
import { Grid2 as Grid, Typography } from '@mui/material';
import { FormikCurrencyAutocomplete } from '@shared/Formik/FormikCurrencyAutocomplete';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { tomorrow } from '@utils/utils';
import { Field } from 'formik';
import { ReactElement } from 'react';
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
  return (
    <PaperContainer>
      <Title>
        <Typography variant="h6">{t('Parameters')}</Typography>
      </Title>
      <Grid spacing={3} container>
        <Grid size={{ xs: 3 }}>
          <Field
            name="dispersionStartDate"
            label={t('Dispersion Start Date')}
            component={FormikDateField}
            required
            fullWidth
            decoratorEnd={<CalendarTodayRounded color="disabled" />}
            dataCy="input-dispersion-start-date"
            tooltip={t('The first day from which payments could be delivered.')}
          />
        </Grid>
        <Grid size={{ xs: 3 }}>
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
        <Grid size={{ xs: 3 }}>
          <Field
            name="currency"
            component={FormikCurrencyAutocomplete}
            required
            disabled={Boolean(paymentPlan?.isFollowUp)}
          />
        </Grid>
      </Grid>
    </PaperContainer>
  );
};
