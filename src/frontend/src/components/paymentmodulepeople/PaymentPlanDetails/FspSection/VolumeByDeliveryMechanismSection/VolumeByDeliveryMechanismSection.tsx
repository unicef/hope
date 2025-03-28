import { Box, Grid2 as Grid, Typography } from '@mui/material';
import { Pie } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LabelizedField } from '@core/LabelizedField';
import { FieldBorder } from '@core/FieldBorder';
import type { ChartData, ChartOptions } from 'chart.js';
import { FC } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

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
  paymentPlan: PaymentPlanDetail;
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
  const { volume_by_delivery_mechanism } = paymentPlan;

  const mappedDeliveryMechanism = volume_by_delivery_mechanism?.map(
    (vdm, index) => (
      <Grid
        size={{ xs: 6 }}
        /* eslint-disable-next-line react/no-array-index-key */
        key={`${vdm.delivery_mechanism.id}-${index}`}
      >
        <FieldBorder
          color={getDeliveryMechanismColor(vdm.delivery_mechanism.name)}
        >
          <LabelizedField
            label={`${vdm.delivery_mechanism.name} (${vdm.delivery_mechanism.fsp?.name ?? '-'})`}
            value={`${vdm.volume ?? '0.00'} ${paymentPlan.currency} (${vdm.volume_usd ?? '0.00'} USD)`}
          />
        </FieldBorder>
      </Grid>
    ),
  );

  const chartLabels = volume_by_delivery_mechanism.map(
    (el) => `${el.deliveryMechanism.name} (${el.deliveryMechanism.fsp?.name})`,
  );

  const chartData = volume_by_delivery_mechanism.map((el) => el.volumeUsd);

  const chartColors = (): string[] => {
    return volume_by_delivery_mechanism.map((el) =>
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
