import { Title } from '@core/Title';
import { Grid, Typography } from '@mui/material';
import { CalendarTodayRounded } from '@mui/icons-material';
import { FormikCurrencyAutocomplete } from '@shared/Formik/FormikCurrencyAutocomplete';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { tomorrow } from '@utils/utils';
import { Field, useFormikContext } from 'formik';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PaperContainer } from '../../../targeting/PaperContainer';

interface PaymentPlanParametersProps {
  values;
  paymentPlan?;
  cycles?: Array<{ id: string; title: string | null }>;
  groups?: Array<{ id: string; name?: string }>;
  onCycleChange?: (cycleId: string) => void;
}

export const PaymentPlanParameters = ({
  values,
  paymentPlan,
  cycles,
  groups,
  onCycleChange,
}: PaymentPlanParametersProps): ReactElement => {
  const { t } = useTranslation();
  const { setFieldValue } = useFormikContext();
  return (
    <PaperContainer>
      <Title>
        <Typography variant="h6">{t('Parameters')}</Typography>
      </Title>
      <Grid spacing={3} container>
        {cycles && (
          <Grid size={{ xs: 3 }}>
            <Field
              name="programCycle"
              label={t('Cycle')}
              fullWidth
              variant="outlined"
              required
              choices={cycles.map((c) => ({ value: c.id, name: c.title ?? c.id }))}
              component={FormikSelectField}
              disableClearable
              onChange={(e) => {
                setFieldValue('paymentPlanGroupId', '');
                onCycleChange?.(e.target.value);
              }}
              data-cy="input-program-cycle"
            />
          </Grid>
        )}
        {groups && (
          <Grid size={{ xs: 3 }}>
            <Field
              name="paymentPlanGroupId"
              label={t('Group')}
              fullWidth
              variant="outlined"
              required
              choices={groups.map((g) => ({ value: g.id, name: g.name ?? g.id }))}
              component={FormikSelectField}
              data-cy="input-payment-plan-group"
            />
          </Grid>
        )}
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
