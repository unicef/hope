import { Box, Button, Grid, Typography } from '@material-ui/core';
import { Link } from 'react-router-dom';
import React from 'react';
import { Pie } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { MiśTheme } from '../../../../theme';
import { TargetPopulationQuery } from '../../../../__generated__/graphql';
import { DividerLine } from '../../../core/DividerLine';
import { LabelizedField } from '../../../core/LabelizedField';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { FspRow } from './FspRow';

const colors = {
  mobileMoney: '#023E90',
  transfer: '#73C304',
  cash: '#039BFE',
  wallet: '#F2E82D',
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

interface VolumeByDeliveryProps {
  resultsData?:
    | TargetPopulationQuery['targetPopulation']['candidateStats']
    | TargetPopulationQuery['targetPopulation']['finalStats'];
}

export function VolumeByDelivery({
  resultsData,
}: VolumeByDeliveryProps): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  if (!resultsData) {
    return null;
  }
  return (
    <>
      <PaperContainer>
        <Title>
          <Typography variant='h6'>
            {t('Volume by Delivery Mechanism in')} PLN (USD)
          </Typography>
        </Title>
        <ContentWrapper>
          <Grid container spacing={0} justify='flex-start'>
            <Grid item xs={6}>
              <FieldBorder color={colors.mobileMoney}>
                <LabelizedField
                  label={t('Mobile Money')}
                  value={resultsData.childFemale}
                />
              </FieldBorder>
            </Grid>
            <Grid item xs={6}>
              <FieldBorder color={colors.transfer}>
                <LabelizedField
                  label={t('Transfer')}
                  value={resultsData.adultFemale}
                />
              </FieldBorder>
            </Grid>
            <Grid item xs={6}>
              <FieldBorder color={colors.cash}>
                <LabelizedField
                  label={t('Cash')}
                  value={resultsData.childMale}
                />
              </FieldBorder>
            </Grid>
            <Grid item xs={6}>
              <FieldBorder color={colors.wallet}>
                <LabelizedField
                  label={t('Wallet')}
                  value={resultsData.adultMale}
                />
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
                      t('Female Children'),
                      t('Female Adults'),
                      t('Male Children'),
                      t('Male Adults'),
                    ],
                    datasets: [
                      {
                        data: [
                          resultsData.childFemale,
                          resultsData.adultFemale,
                          resultsData.childMale,
                          resultsData.adultMale,
                        ],
                        backgroundColor: [
                          colors.mobileMoney,
                          colors.transfer,
                          colors.cash,
                          colors.wallet,
                        ],
                      },
                    ],
                  }}
                />
              </ChartContainer>
            </Grid>
          </Grid>
        </ContentWrapper>
        <DividerLine />
        <Title>
          <Box display='flex' justifyContent='space-between'>
            <Typography variant='h6'>{t('FSPs')}</Typography>
            <Button component={Link} to={`/${businessArea}/payment-module`}>
              {t('Preview')}
            </Button>
          </Box>
        </Title>
        <Box display='flex' flexDirection='column'>
          {[
            {
              id: 1,
              name: 'CITIGROUP',
              maxAmount: 10000,
              deliveryMechanism: 'Mobile Money',
            },
            {
              id: 2,
              name: 'Bank of America',
              maxAmount: 2222,
              deliveryMechanism: 'Transfer',
            },
            {
              id: 3,
              name: 'Chase Bank',
              maxAmount: 4566,
              deliveryMechanism: 'Cash',
            },
          ].map((el) => (
            <FspRow key={el.id} fsp={el} />
          ))}
        </Box>
      </PaperContainer>
    </>
  );
}
