import { Title } from '@core/Title';
import { Typography } from '@mui/material';
import { CalendarTodayRounded } from '@mui/icons-material';
import { FormikCurrencyAutocomplete } from '@shared/Formik/FormikCurrencyAutocomplete';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { tomorrow } from '@utils/utils';
import { Field } from 'formik';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

interface PaymentPlanParametersProps {
  values;
  paymentPlan?;
  cycles?: Array<{ id: string; title: string | null }>;
}

export const PaymentPlanParameters = ({
  values,
  paymentPlan,
  cycles,
}: PaymentPlanParametersProps): ReactElement => {
  const { t } = useTranslation();
  return (
    <PaperContainer>
      <Title>
        <Typography variant="h6">{t('Parameters')}</Typography>
      </Title>
      <ResponsiveGridContainer spacing={3}>
        {cycles && (
          <ResponsiveGrid size="quarter">
            <Field
              name="programCycle"
              label={t('Cycle')}
              fullWidth
              variant="outlined"
              required
              choices={cycles.map((c) => ({
                value: c.id,
                name: c.title ?? c.id,
              }))}
              component={FormikSelectField}
              disableClearable
              data-cy="input-program-cycle"
            />
          </ResponsiveGrid>
        )}
        <ResponsiveGrid size="quarter" mobileSize="half">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter" mobileSize="half">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="quarter">
          <Field
            name="currency"
            component={FormikCurrencyAutocomplete}
            required
            disabled={paymentPlan?.planType === 'FOLLOW_UP'}
          />
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </PaperContainer>
  );
};
