import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { Pie } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';
import { LabelizedField } from '../../../../core/LabelizedField';
import { Missing } from '../../../../core/Missing';

const colors = {
  femaleChildren: '#5F02CF',
  maleChildren: '#1D6A64',
  femaleAdult: '#DFCCF5',
  maleAdult: '#B1E3E0',
};

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

export const VolumeByDeliveryMechanismSection = ({
  paymentPlan,
}: VolumeByDeliveryMechanismSectionProps): React.ReactElement => {
  const { t } = useTranslation();
  const {
    femaleChildrenCount,
    maleChildrenCount,
    femaleAdultsCount,
    maleAdultsCount,
  } = paymentPlan;

  return (
    <>
      <Box display='flex' flexDirection='column'>
        <Title>
          <Typography variant='h6'>
            {t('Volume by Delivery Mechanism')} in <Missing />
          </Typography>{' '}
        </Title>
        <ContentWrapper>
          <Grid container spacing={0} justify='flex-start'>
            <Grid item xs={6}>
              <FieldBorder color={colors.femaleChildren}>
                <LabelizedField
                  label={t('Bank Transfer')}
                  value={femaleChildrenCount}
                />
              </FieldBorder>
            </Grid>
            <Grid item xs={6}>
              <FieldBorder color={colors.femaleAdult}>
                <LabelizedField
                  label={t('E-wallet')}
                  value={femaleAdultsCount}
                />
              </FieldBorder>
            </Grid>
            <Grid item xs={6}>
              <FieldBorder color={colors.maleChildren}>
                <LabelizedField
                  label={t('Mobile Money')}
                  value={maleChildrenCount}
                />
              </FieldBorder>
            </Grid>
            <Grid item xs={6}>
              <FieldBorder color={colors.maleAdult}>
                <LabelizedField label={t('Cash')} value={maleAdultsCount} />
              </FieldBorder>
            </Grid>
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
                    labels: [
                      t('Bank Transfer'),
                      t('E-wallet'),
                      t('Mobile Money'),
                      t('Cash'),
                    ],
                    datasets: [
                      {
                        data: [
                          femaleChildrenCount,
                          femaleAdultsCount,
                          maleChildrenCount,
                          maleAdultsCount,
                        ],
                        backgroundColor: [
                          colors.femaleChildren,
                          colors.femaleAdult,
                          colors.maleChildren,
                          colors.maleAdult,
                        ],
                      },
                    ],
                  }}
                />
              </ChartContainer>
            </Grid>
          </Grid>
        </ContentWrapper>
      </Box>
    </>
  );
};
