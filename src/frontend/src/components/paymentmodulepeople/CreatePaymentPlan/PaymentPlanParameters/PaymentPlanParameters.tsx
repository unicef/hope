import { OverviewContainer } from '@core/OverviewContainer';
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
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface PaymentPlanParametersProps {
  values;
  paymentPlan?;
}

export const PaymentPlanParameters = ({
  values,
  paymentPlan,
}: PaymentPlanParametersProps): ReactElement => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();

  const { data, isLoading: loading } = useQuery({
    queryKey: ['targetPopulation', values.targetingId, businessArea, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsTargetPopulationsRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
        id: values.targetingId,
      }),
    enabled: !!values.targetingId && !!businessArea && !!programId,
  });

  const { data: programData, isLoading: loadingProgram } =
    useQuery<ProgramDetail>({
      queryKey: ['program', businessArea, programId],
      queryFn: () =>
        RestService.restBusinessAreasProgramsRetrieve({
          businessAreaSlug: businessArea,
          slug: programId,
        }),
      enabled: !!businessArea && !!programId,
    });

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
              minDate={programData?.startDate}
              maxDate={values.endDate || programData?.endDate}
              disabled={
                !data ||
                loading ||
                loadingProgram ||
                Boolean(paymentPlan?.isFollowUp)
              }
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
              maxDate={programData?.endDate}
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
              disabled={!data || loading || loadingProgram}
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
