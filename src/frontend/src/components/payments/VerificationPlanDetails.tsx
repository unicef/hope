import { Box, Grid2 as Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  CashPlanVerificationSamplingChoicesQuery,
  PaymentPlanQuery,
} from '@generated/graphql';
import { choicesToDict, paymentVerificationStatusToColor } from '@utils/utils';
import { LabelizedField } from '@core/LabelizedField';
import { StatusBox } from '@core/StatusBox';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { VerificationPlanActions } from './VerificationPlanActions';
import { VerificationPlanDetailsChart } from './VerificationPlanChart';
import { AdminButton } from '@core/AdminButton';
import { ReactElement } from 'react';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
  flex-direction: column;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;
`;

interface VerificationPlanDetailsProps {
  verificationPlan: PaymentPlanQuery['paymentPlan']['verificationPlans']['edges'][0]['node'];
  samplingChoicesData: CashPlanVerificationSamplingChoicesQuery;
  planNode: PaymentPlanQuery['paymentPlan'];
}

export function VerificationPlanDetails({
  verificationPlan,
  samplingChoicesData,
  planNode,
}: VerificationPlanDetailsProps): ReactElement {
  const { t } = useTranslation();

  const samplingChoicesDict = choicesToDict(
    samplingChoicesData.cashPlanVerificationSamplingChoices,
  );
  return (
    <Container>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Title>
          <Typography data-cy={`verification-plan-${verificationPlan.unicefId}`} variant="h6">
            {t('Verification Plan')} #{verificationPlan.unicefId}
            <AdminButton adminUrl={verificationPlan.adminUrl} sx={{ ml: 2 }} />
          </Typography>
        </Title>
        <VerificationPlanActions
          verificationPlan={verificationPlan}
          samplingChoicesData={samplingChoicesData}
          planNode={planNode}
        />
      </Box>
      <Grid container>
        <Grid size={{ xs:9 }}>
          <Grid container spacing={3}>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('STATUS')}>
                <StatusBox
                  status={verificationPlan.status}
                  statusToColor={paymentVerificationStatusToColor}
                  dataCy="verification-plan-status"
                />
              </LabelizedField>
            </Grid>
            {[
              {
                label: t('SAMPLING'),
                value: samplingChoicesDict[verificationPlan.sampling],
              },
              {
                label: t('RESPONDED'),
                value: verificationPlan.respondedCount,
              },
              {
                label: t('RECEIVED WITH ISSUES'),
                value: verificationPlan.receivedWithProblemsCount,
              },
              {
                label: t('VERIFICATION CHANNEL'),
                value: verificationPlan.verificationChannel,
              },
              {
                label: t('SAMPLE SIZE'),
                value: verificationPlan.sampleSize,
              },
              {
                label: t('RECEIVED'),
                value: verificationPlan.receivedCount,
              },
              {
                label: t('NOT RECEIVED'),
                value: verificationPlan.notReceivedCount,
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
              <Grid size={{ xs:3 }} key={el.label}>
                <LabelizedField label={el.label} value={el.value} />
              </Grid>
            ))}
          </Grid>
        </Grid>
        <Grid size={{ xs: 3 }}>
          <VerificationPlanDetailsChart verificationPlan={verificationPlan} />
        </Grid>
      </Grid>
    </Container>
  );
}
