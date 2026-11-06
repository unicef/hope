import { BlackLink } from '@components/core/BlackLink';
import { RelatedFollowUpPaymentLists } from '@components/paymentmodule/PaymentListDetails/PaymentListDetails/RelatedFollowUpPaymentLists';
import { RelatedTopUpPaymentLists } from '@components/paymentmodule/PaymentListDetails/PaymentListDetails/RelatedTopUpPaymentLists';
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
import type { PaymentListDetail } from '@restgenerated/models/PaymentListDetail';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { ResponsiveGrid, responsiveValue } from 'src/responsive';
interface PaymentListDetailsProps {
  baseUrl: string;
  paymentList: PaymentListDetail;
}

export const PaymentListDetails = ({
  baseUrl,
  paymentList,
}: PaymentListDetailsProps): ReactElement => {
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
    paymentPlan,
  } = paymentList;

  return (
    <Grid size={{ xs: 12 }}>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">{t('Details')}</Typography>
        </Title>
        <OverviewContainer>
          <Grid container>
            <Grid
              container
              size={responsiveValue(12, 9)}
              spacing={responsiveValue(3, 6)}
            >
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Created By')}>
                  {createdBy}
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Programme')}>
                  <BlackLink to={`/${baseUrl}/details/${program.code}`}>
                    {program.name}
                  </BlackLink>
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Target Population')}>
                  <BlackLink
                    to={`/${baseUrl}/target-population/${paymentList.id}`}
                  >
                    {paymentList.name}
                  </BlackLink>
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Currency')}>
                  {currency}
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Payment Plan')}>
                  {paymentPlan ? (
                    <BlackLink
                      to={`/${baseUrl}/payment-module/payment-plans/${paymentPlan.id}`}
                    >
                      {paymentPlan.name}
                    </BlackLink>
                  ) : (
                    '-'
                  )}
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Start Date')}>
                  <UniversalMoment>{startDate}</UniversalMoment>
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('End Date')}>
                  <UniversalMoment>{endDate}</UniversalMoment>
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Dispersion Start Date')}>
                  <UniversalMoment>{dispersionStartDate}</UniversalMoment>
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <LabelizedField label={t('Dispersion End Date')}>
                  <UniversalMoment>{dispersionEndDate}</UniversalMoment>
                </LabelizedField>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <Box
                  sx={{
                    mr: 1,
                  }}
                >
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
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <Box
                  sx={{
                    mr: 1,
                  }}
                >
                  <LabelizedField label={t('FSP')}>
                    {paymentList.financialServiceProvider?.name}
                  </LabelizedField>
                </Box>
              </ResponsiveGrid>
              <ResponsiveGrid size="quarter" mobileSize="half">
                <Box
                  sx={{
                    mr: 1,
                  }}
                >
                  <LabelizedField label={t('Delivery Mechanism')}>
                    {paymentList.deliveryMechanism?.name}
                  </LabelizedField>
                </Box>
              </ResponsiveGrid>
              {paymentList.sourcePaymentList && (
                <ResponsiveGrid size="quarter" mobileSize="half">
                  <LabelizedField label={t('Main Payment List')}>
                    <BlackLink
                      to={`/${baseUrl}/payment-module/payment-lists/${paymentList.sourcePaymentList.id}`}
                    >
                      {paymentList.sourcePaymentList.unicefId}
                    </BlackLink>
                  </LabelizedField>
                </ResponsiveGrid>
              )}
              {paymentList.paymentPlanPurposes?.length > 0 && (
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
                      {paymentList.paymentPlanPurposes.map((p) => (
                        <Chip key={p.id} label={p.name} size="small" />
                      ))}
                    </Box>
                  </LabelizedField>
                </Grid>
              )}
            </Grid>
            <Grid
              container
              sx={{ flexDirection: 'column', mt: responsiveValue(6, 0) }}
              size={responsiveValue(12, 3)}
              spacing={responsiveValue(3, 6)}
            >
              <Grid size={{ xs: 12 }}>
                <FieldBorder color="#84A1CA">
                  <RelatedFollowUpPaymentLists
                    followUps={followUps}
                    baseUrl={baseUrl}
                  />
                </FieldBorder>
              </Grid>
              <Grid size={{ xs: 12 }}>
                <FieldBorder color="#84A1CA">
                  <RelatedTopUpPaymentLists topUps={topUps} baseUrl={baseUrl} />
                </FieldBorder>
              </Grid>
            </Grid>
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
};
