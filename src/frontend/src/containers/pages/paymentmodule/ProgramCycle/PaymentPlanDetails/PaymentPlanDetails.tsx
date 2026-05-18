import { BlackLink } from '@components/core/BlackLink';
import { RelatedFollowUpPaymentPlans } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetails/RelatedFollowUpPaymentPlans';
import { RelatedTopUpPaymentPlans } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetails/RelatedTopUpPaymentPlans';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { FieldBorder } from '@core/FieldBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { Info } from '@mui/icons-material';
import {
  Box,
  Chip,
  Grid,
  IconButton,
  Tooltip,
  Typography,
} from '@mui/material';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
interface PaymentPlanDetailsProps {
  baseUrl: string;
  paymentPlan: PaymentPlanDetail;
}

export const PaymentPlanDetails = ({
  baseUrl,
  paymentPlan,
}: PaymentPlanDetailsProps): ReactElement => {
  const { t } = useTranslation();
  const {
    createdBy,
    currency,
    startDate,
    endDate,
    dispersionStartDate,
    dispersionEndDate,
    exchangeRate,
    followUps,
    topUps,
    program,
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
                  {createdBy}
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Programme')}>
                  <BlackLink to={`/${baseUrl}/details/${program.code}`}>
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
                <LabelizedField label={t('Group')}>
                  {paymentPlan.paymentPlanGroup ? (
                    <BlackLink
                      to={`/${baseUrl}/payment-module/groups/${paymentPlan.paymentPlanGroup.id}`}
                    >
                      {paymentPlan.paymentPlanGroup.name}
                    </BlackLink>
                  ) : (
                    '-'
                  )}
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
                  <UniversalMoment>{dispersionStartDate}</UniversalMoment>
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Dispersion End Date')}>
                  <UniversalMoment>{dispersionEndDate}</UniversalMoment>
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <Box mr={1}>
                  <LabelizedField label={t('FX Rate Applied')}>
                    {exchangeRate}
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
              <Grid size={{ xs: 3 }}>
                <Box mr={1}>
                  <LabelizedField label={t('FSP')}>
                    {paymentPlan.financialServiceProvider.name}
                  </LabelizedField>
                </Box>
              </Grid>
              <Grid size={{ xs: 3 }}>
                <Box mr={1}>
                  <LabelizedField label={t('Delivery Mechanism')}>
                    {paymentPlan.deliveryMechanism.name}
                  </LabelizedField>
                </Box>
              </Grid>
              {paymentPlan.paymentPlanPurposes?.length > 0 && (
                <Grid size={{ xs: 12 }}>
                  <LabelizedField label={t('Purposes')}>
                    <Box
                      sx={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: 0.5,
                        alignItems: 'center',
                      }}
                    >
                      {paymentPlan.paymentPlanPurposes.map((p) => (
                        <Chip key={p.id} label={p.name} size="small" />
                      ))}
                    </Box>
                  </LabelizedField>
                </Grid>
              )}
            </Grid>
            <Grid container direction="column" size={{ xs: 3 }} spacing={6}>
              <Grid size={{ xs: 12 }}>
                <FieldBorder color="#84A1CA">
                  <RelatedFollowUpPaymentPlans
                    followUps={followUps}
                    baseUrl={baseUrl}
                  />
                </FieldBorder>
              </Grid>
              <Grid size={{ xs: 12 }}>
                <FieldBorder color="#84A1CA">
                  <RelatedTopUpPaymentPlans
                    topUps={topUps}
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
