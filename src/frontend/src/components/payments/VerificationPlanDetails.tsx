import { AdminButton } from '@core/AdminButton';
import { LabelizedField } from '@core/LabelizedField';
import { StatusBox } from '@core/StatusBox';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { Box, Typography, Grid } from '@mui/material';
import type { PaymentVerificationPlanDetails } from '@restgenerated/models/PaymentVerificationPlanDetails';
import { formatFigure, paymentVerificationStatusToColor } from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { VerificationPlanActions } from './VerificationPlanActions';
import { VerificationPlanDetailsChart } from './VerificationPlanChart';
import {
  ResponsiveGrid,
  ResponsiveGridContainer,
  SECTION_PADDING,
  responsiveValue,
} from 'src/responsive';

const Container = styled(Box)`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  flex-direction: column;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;
`;

interface VerificationPlanDetailsProps {
  verificationPlan: PaymentVerificationPlanDetails['paymentVerificationPlans'][number];
  paymentPlanNode: PaymentVerificationPlanDetails;
}

export function VerificationPlanDetails({
  verificationPlan,
  paymentPlanNode,
}: VerificationPlanDetailsProps): ReactElement {
  const { t } = useTranslation();

  return (
    <Container sx={{ padding: SECTION_PADDING }}>
      <Box
        sx={{
          display: 'flex',
          flexDirection: responsiveValue('column', 'row'),
          alignItems: responsiveValue('stretch', 'center'),
          justifyContent: 'space-between',
        }}
      >
        <Title>
          <Typography
            data-cy={`verification-plan-${verificationPlan.unicefId}`}
            variant="h6"
          >
            {t('Verification Plan')} #{verificationPlan.unicefId}
            <AdminButton adminUrl={verificationPlan.adminUrl} sx={{ ml: 2 }} />
          </Typography>
        </Title>
        <VerificationPlanActions
          verificationPlan={verificationPlan}
          paymentPlanNode={paymentPlanNode}
        />
      </Box>
      <Grid container rowSpacing={responsiveValue(4, 0)}>
        <Grid size={responsiveValue(12, 9)}>
          <ResponsiveGridContainer spacing={3}>
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField label={t('STATUS')}>
                <StatusBox
                  status={verificationPlan.status}
                  statusToColor={paymentVerificationStatusToColor}
                  dataCy="verification-plan-status"
                />
              </LabelizedField>
            </ResponsiveGrid>
            {[
              {
                label: t('SAMPLING'),
                value: verificationPlan.sampling,
              },
              {
                label: t('RESPONDED'),
                value: formatFigure(verificationPlan.respondedCount),
              },
              {
                label: t('RECEIVED WITH ISSUES'),
                value: formatFigure(verificationPlan.receivedWithProblemsCount),
              },
              {
                label: t('VERIFICATION CHANNEL'),
                value: verificationPlan.verificationChannel,
              },
              {
                label: t('SAMPLE SIZE'),
                value: formatFigure(verificationPlan.sampleSize),
              },
              {
                label: t('RECEIVED'),
                value: formatFigure(verificationPlan.receivedCount),
              },
              {
                label: t('NOT RECEIVED'),
                value: formatFigure(verificationPlan.notReceivedCount),
              },
              {
                label: t('ACTIVATION DATE'),
                value: (
                  <UniversalMoment>
                    {verificationPlan.activationDate}
                  </UniversalMoment>
                ),
              },
              {
                label: t('COMPLETION DATE'),
                value: (
                  <UniversalMoment>
                    {verificationPlan.completionDate}
                  </UniversalMoment>
                ),
              },
            ].map((el) => (
              <ResponsiveGrid size="quarter" mobileSize="half" key={el.label}>
                <LabelizedField label={el.label} value={el.value} />
              </ResponsiveGrid>
            ))}
          </ResponsiveGridContainer>
        </Grid>
        <Grid
          size={responsiveValue(12, 3)}
          sx={{ minHeight: responsiveValue(160, 0) }}
        >
          <VerificationPlanDetailsChart verificationPlan={verificationPlan} />
        </Grid>
      </Grid>
    </Container>
  );
}
