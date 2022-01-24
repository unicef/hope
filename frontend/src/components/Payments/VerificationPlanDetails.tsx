import { Typography, Grid, Box } from '@material-ui/core';
import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  choicesToDict,
  paymentVerificationStatusToColor,
} from '../../utils/utils';
import {
  CashPlanQuery,
  CashPlanVerificationSamplingChoicesQuery,
} from '../../__generated__/graphql';
import { LabelizedField } from '../LabelizedField';
import { StatusBox } from '../StatusBox';
import { UniversalMoment } from '../UniversalMoment';

interface VerificationPlanDetailsProps {
  verificationPlan: CashPlanQuery['cashPlan']['verifications']['edges'][number]['node'];
  samplingChoicesData: CashPlanVerificationSamplingChoicesQuery;
}

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: column;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

const ChartContainer = styled.div`
  width: 150px;
  height: 150px;
`;

export const VerificationPlanDetails = ({
  verificationPlan,
  samplingChoicesData,
}: VerificationPlanDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  const samplingChoicesDict = choicesToDict(
    samplingChoicesData.cashPlanVerificationSamplingChoices,
  );

  return (
    <Container>
      <Title>
        <Typography variant='h6'>{t('Verification Plan Details')}</Typography>
      </Title>
      <Grid container>
        <Grid item xs={11}>
          <Grid container>
            <Grid item xs={3}>
              <LabelizedField label={t('STATUS')}>
                <StatusContainer>
                  <StatusBox
                    status={verificationPlan.status}
                    statusToColor={paymentVerificationStatusToColor}
                  />
                </StatusContainer>
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
                label: t('VERIFICATION METHOD'),
                value: verificationPlan.verificationMethod,
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
              <Grid item xs={3} key={el.label}>
                <Box pt={2} pb={2}>
                  <LabelizedField label={el.label} value={el.value} />
                </Box>
              </Grid>
            ))}
          </Grid>
        </Grid>
        <Grid item xs={1}>
          <ChartContainer>
            <Doughnut
              width={200}
              height={200}
              options={{
                maintainAspectRatio: false,
                cutoutPercentage: 80,
                legend: {
                  display: false,
                },
              }}
              data={{
                labels: [
                  t('RECEIVED'),
                  t('RECEIVED WITH ISSUES'),
                  t('NOT RECEIVED'),
                  t('PENDING'),
                ],
                datasets: [
                  {
                    data: [
                      verificationPlan.receivedCount,
                      verificationPlan.receivedWithProblemsCount,
                      verificationPlan.notReceivedCount,
                      verificationPlan.sampleSize -
                        verificationPlan.respondedCount,
                    ],
                    backgroundColor: [
                      '#31D237',
                      '#F57F1A',
                      '#FF0100',
                      '#DCDCDC',
                    ],
                    hoverBackgroundColor: [
                      '#31D237',
                      '#F57F1A',
                      '#FF0100',
                      '#DCDCDC',
                    ],
                  },
                ],
              }}
            />
          </ChartContainer>
        </Grid>
      </Grid>
    </Container>
  );
};
