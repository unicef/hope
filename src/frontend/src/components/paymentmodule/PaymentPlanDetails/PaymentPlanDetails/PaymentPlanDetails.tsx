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
import { FieldBorder } from '@core/FieldBorder';
import { RelatedFollowUpPaymentPlans } from './RelatedFollowUpPaymentPlans';
import { Info } from '@mui/icons-material';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

interface PaymentPlanDetailsProps {
  baseUrl: string;
  paymentPlan: PaymentPlanDetail;
}

const PaymentPlanDetails = ({
  baseUrl,
  paymentPlan,
}: PaymentPlanDetailsProps): ReactElement => {
  const { t } = useTranslation();
  const {
    created_by,
    program,
    currency,
    start_date,
    end_date,
    exchange_rate,
    dispersion_start_date,
    dispersion_end_date,
    follow_ups,
  } = paymentPlan;

  return (
    <Grid size={{ xs: 12 }}>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">{t('Details')}</Typography>
        </Title>
        <OverviewContainer>
          <Grid container>
            <Grid container size={{ xs: 9 }} spacing={6}>
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
                  <BlackLink
                    to={`/${baseUrl}/target-population/${paymentPlan.id}`}
                  >
                    {paymentPlan.name}
                  </BlackLink>
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Currency')}>
                  {currency}
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Start Date')}>
                  <UniversalMoment>{startDate}</UniversalMoment>
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('End Date')}>
                  <UniversalMoment>{endDate}</UniversalMoment>
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Dispersion Start Date')}>
                  <UniversalMoment>{dispersion_start_date}</UniversalMoment>
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Dispersion End Date')}>
                  <UniversalMoment>{dispersion_end_date}</UniversalMoment>
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
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
              </Grid>
            </Grid>
            <Grid container direction="column" size={{ xs: 3 }} spacing={6}>
              <Grid size={{ xs: 12 }}>
                <FieldBorder color="#84A1CA">
                  <RelatedFollowUpPaymentPlans
                    followUps={follow_ups}
                    baseUrl={baseUrl}
                  />
                </FieldBorder>
              </Grid>
            </Grid>
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
};

export default withErrorBoundary(PaymentPlanDetails, 'PaymentPlanDetails');
