import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { Pie } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';
import { LabelizedField } from '../../../../core/LabelizedField';

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

const ContentWrapper = styled.div`
  display: flex;
`;

const FieldBorder = styled.div`
  padding: 0 ${({ theme }) => theme.spacing(2)}px;
  border-color: ${(props) => props.color};
  border-left-width: 2px;
  border-left-style: solid;
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

export const VolumeByDeliveryMechanismSection = ({
  paymentPlan,
}: VolumeByDeliveryMechanismSectionProps): React.ReactElement => {
  const { t } = useTranslation();
  const { volumeByDeliveryMechanism } = paymentPlan;

  const mappedDeliveryMechanism = volumeByDeliveryMechanism.map((vdm, index) => (
    <Grid
      item
      xs={6}
      /* eslint-disable-next-line react/no-array-index-key */
      key={`${vdm.deliveryMechanism.id}-${index}`}
    >
      <FieldBorder color={getDeliveryMechanismColor(vdm.deliveryMechanism.name)}>
        <LabelizedField
          label={`${vdm.deliveryMechanism.name} (${vdm.deliveryMechanism.fsp?.name})`}
          value={vdm.volumeUsd}
        />
      </FieldBorder>
    </Grid>
  ));

  const chartLabels = volumeByDeliveryMechanism.map(
    (el) => `${el.deliveryMechanism.name} (${el.deliveryMechanism.fsp?.name})`,
  );

  const chartData = volumeByDeliveryMechanism.map((el) => el.volumeUsd);

  const chartColors = (): string[] => {
    const defaultColorsArray = volumeByDeliveryMechanism.map((el) =>
      getDeliveryMechanismColor(el.deliveryMechanism.name),
    );

    return defaultColorsArray;
  };

  return (
    <Box display='flex' flexDirection='column'>
      <Title>
        <Typography variant='h6'>
          {t('Volume by Delivery Mechanism')} in USD
        </Typography>{' '}
      </Title>
      <ContentWrapper>
        <Grid container spacing={0} justify='flex-start'>
          {mappedDeliveryMechanism}
        </Grid>
        <Grid container spacing={0} justify='flex-start' alignItems='center'>
          <Grid item xs={4}>
            <ChartContainer>
              <Pie
                width={100}
                height={100}
                options={{
                  legend: {
                    display: false,
                  },
                }}
                data={{
                  labels: chartLabels,
                  datasets: [
                    {
                      data: chartData,
                      backgroundColor: chartColors,
                    },
                  ],
                }}
              />
            </ChartContainer>
          </Grid>
        </Grid>
      </ContentWrapper>
    </Box>
  );
};
