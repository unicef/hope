import { Doughnut } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

interface VerificationPlanDetailsChartProps {
  verificationPlan: PaymentPlanDetail['verificationPlans']['edges'][0]['node'];
}

const ChartContainer = styled.div`
  width: 100%;
  height: 100%;
`;

export function VerificationPlanDetailsChart({
  verificationPlan,
}: VerificationPlanDetailsChartProps): ReactElement {
  const { t } = useTranslation();
  return (
    <ChartContainer>
      <Doughnut
        options={
          {
            maintainAspectRatio: false,
            cutout: '%',
            plugins: {
              legend: {
                display: false,
              },
            },
          } as any
        }
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
                verificationPlan.sampleSize - verificationPlan.respondedCount,
              ],
              backgroundColor: ['#31D237', '#F57F1A', '#FF0100', '#DCDCDC'],
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
  );
}
