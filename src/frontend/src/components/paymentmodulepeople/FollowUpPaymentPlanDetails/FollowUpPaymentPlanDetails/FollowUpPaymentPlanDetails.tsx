import {
  Box,
  Grid2 as Grid,
  IconButton,
  Tooltip,
  Typography,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { renderUserName } from '@utils/utils';
import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { Info } from '@mui/icons-material';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

interface FollowUpPaymentPlanDetailsProps {
  baseUrl: string;
  paymentPlan: PaymentPlanDetail;
}

export function FollowUpPaymentPlanDetails({
  baseUrl,
  paymentPlan,
}: FollowUpPaymentPlanDetailsProps): ReactElement {
  const { t } = useTranslation();
  const {
    id,
    name,
    createdBy,
    program,
    currency,
    startDate,
    endDate,
    dispersionStartDate,
    dispersionEndDate,
    source_payment_plan: {
      id: sourcePaymentPlanId,
      unicef_id: sourcePaymentPlanUnicefId,
    },
    exchangeRate,
  } = paymentPlan;

  return (
    <Grid size={{ xs: 12 }}>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">{t('Details')}</Typography>
        </Title>
        <OverviewContainer>
          <Grid container spacing={6}>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Main Payment Plan')}>
                <BlackLink
                  to={`/${baseUrl}/payment-module/payment-plans/${sourcePaymentPlanId}`}
                >
                  {sourcePaymentPlanUnicefId}
                </BlackLink>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Created By')}>
                {renderUserName(created_by)}
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Programme')}>
                <BlackLink to={`/${baseUrl}/details/${program.id}`}>
                  {program.name}
                </BlackLink>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Target Population')}>
                <BlackLink to={`/${baseUrl}/target-population/${id}`}>
                  {name}
                </BlackLink>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Currency')}>{currency}</LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Start Date')}>
                <UniversalMoment>{startDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('End Date')}>
                <UniversalMoment>{end_date}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Dispersion Start Date')}>
                <UniversalMoment>{dispersion_startDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Dispersion End Date')}>
                <UniversalMoment>{dispersion_end_date}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <Box display="flex" alignItems="center">
                <Box mr={1}>
                  <LabelizedField label={t('FX Rate Applied')}>
                    {exchange_rate}
                  </LabelizedField>
                </Box>
                <Tooltip
                  title={t(
                    'If displayed exchange rate differs from Vision, please contact your designated focal point for resolution',
                  )}
                >
                  <IconButton
                    color="primary"
                    aria-label="exchange-rate"
                    data-cy="info-exchange-rate"
                  >
                    <Info />
                  </IconButton>
                </Tooltip>
              </Box>
            </Grid>
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
}
