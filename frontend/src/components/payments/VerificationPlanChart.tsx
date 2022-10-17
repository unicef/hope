import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { CashPlanOrPaymentPlanQuery } from '../../__generated__/graphql';

interface VerificationPlanDetailsChartProps {
  verificationPlan: CashPlanOrPaymentPlanQuery["cashPlanOrPaymentPlan"]['verificationPlans']['edges'][number]['node'];
}

const ChartContainer = styled.div`
  width: 150px;
  height: 150px;
`;

export const VerificationPlanDetailsChart = ({
  verificationPlan,
}: VerificationPlanDetailsChartProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
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
};
