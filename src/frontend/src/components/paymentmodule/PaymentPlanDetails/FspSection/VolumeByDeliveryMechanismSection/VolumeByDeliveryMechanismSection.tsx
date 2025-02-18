import { Box, Grid2 as Grid, Typography } from '@mui/material';
import { Pie } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentPlanQuery } from '@generated/graphql';
import { LabelizedField } from '@core/LabelizedField';
import { FieldBorder } from '@core/FieldBorder';
import type { ChartData, ChartOptions } from 'chart.js';
import { FC } from 'react';

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(2)};
`;

const ContentWrapper = styled.div`
  display: flex;
`;

const ChartContainer = styled.div`
  width: 100px;
  height: 100px;
  margin: 0 auto;
`;

interface VolumeByDeliveryMechanismSectionProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

const DeliveryMechanismsColorsMap = new Map([
  ['Cardless cash withdrawal', '#FC942A'],
  ['Cash', '#D8E1EE'],
  ['Cash by FSP', '#D8E1EE'],
  ['Cheque', '#10CB16'],
  ['Deposit to Card', '#4E606A'],
  ['In Kind', ' #d8d8d8'],
  ['Mobile Money', '#e4e4e4'],
  ['Other', '#EF4343'],
  ['Pre-paid card', '#D9D1CE'],
  ['Referral', '#715247'],
  ['Transfer', '#003C8F'],
  ['Transfer to Account', '#003C8F'],
  ['Voucher', '#00ADEF'],
]);

export const getDeliveryMechanismColor = (
  deliveryMechanism: string,
): string => {
  if (DeliveryMechanismsColorsMap.has(deliveryMechanism)) {
    return DeliveryMechanismsColorsMap.get(deliveryMechanism);
  }
  return '#CCC';
};

export const VolumeByDeliveryMechanismSection: FC<
  VolumeByDeliveryMechanismSectionProps
> = ({ paymentPlan }) => {
  const { t } = useTranslation();
  const { volumeByDeliveryMechanism } = paymentPlan;

  const mappedDeliveryMechanism = volumeByDeliveryMechanism?.map(
    (vdm, index) => (
      <Grid
        size={{ xs: 6 }}
        /* eslint-disable-next-line react/no-array-index-key */
        key={`${vdm.deliveryMechanism.id}-${index}`}
      >
        <FieldBorder
          color={getDeliveryMechanismColor(vdm.deliveryMechanism.name)}
        >
          <LabelizedField
            label={`${vdm.deliveryMechanism.name} (${vdm.deliveryMechanism.fsp?.name ?? '-'})`}
            value={`${vdm.volume ?? '0.00'} ${paymentPlan.currency} (${vdm.volumeUsd ?? '0.00'} USD)`}
          />
        </FieldBorder>
      </Grid>
    ),
  );

  const chartLabels = volumeByDeliveryMechanism.map(
    (el) => `${el.deliveryMechanism.name} (${el.deliveryMechanism.fsp?.name})`,
  );

  const chartData = volumeByDeliveryMechanism.map((el) => el.volumeUsd);

  const chartColors = (): string[] => {
    return volumeByDeliveryMechanism.map((el) =>
      getDeliveryMechanismColor(el.deliveryMechanism.name),
    );
  };

  const data: ChartData<'pie'> = {
    labels: chartLabels,
    datasets: [
      {
        data: chartData,
        backgroundColor: chartColors(),
      },
    ],
  };

  const options: ChartOptions<'pie'> = {
    plugins: {
      legend: {
        display: false,
      },
    },
  };

  return (
    <Box display="flex" flexDirection="column">
      <Title>
        <Typography variant="h6">
          {t('Volume by Delivery Mechanism')}
        </Typography>{' '}
      </Title>
      <ContentWrapper>
        <Grid container spacing={0} justifyContent="flex-start">
          {mappedDeliveryMechanism}
        </Grid>
        <Grid
          container
          spacing={0}
          justifyContent="flex-start"
          alignItems="center"
        >
          <Grid size={{ xs: 4 }}>
            <ChartContainer>
              <Pie data={data} options={options} />
            </ChartContainer>
          </Grid>
        </Grid>
      </ContentWrapper>
    </Box>
  );
};
