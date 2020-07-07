import React, { useState } from 'react';
import styled from 'styled-components';
import { Button, Grid, Typography, Box } from '@material-ui/core';
import { Doughnut } from 'react-chartjs-2';

import { MiśTheme } from '../../theme';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '../../components/PageHeader';
import { LabelizedField } from '../../components/LabelizedField';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { NewPaymentVerificationDialog } from '../../components/payments/NewPaymentVerificationDialog';
import { UniversalActivityLogTable } from '../tables/UniversalActivityLogTable';
import { EditNewPaymentVerificationDialog } from '../../components/payments/EditNewPaymentVerificationDialog';
import { ActivateVerificationPlan } from '../../components/payments/ActivateVerificationPlan';
import { FinishVerificationPlan } from '../../components/payments/FinishVerificationPlan';
import { DiscardVerificationPlan } from '../../components/payments/DiscardVerificationPlan';

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

const ChartContainer = styled.div`
  width: 100px;
  height: 100px;
`;

const BorderLeftBox = styled.div`
  padding-left: ${({ theme }) => theme.spacing(6)}px;
  border-left: 1px solid #e0e0e0;
  height: 100%;
`;

const BottomTitle = styled.div`
  color: rgba(0, 0, 0, 0.38);
  font-size: 24px;
  line-height: 28px;
  text-align: center;
  padding: 70px;
`;

const TableWrapper = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px;
  padding-bottom: 0;
`;

// interface PaymentVerificationDetailsProps {
//   registration: 'registr';
// }

export function PaymentVerificationDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();

  const [isActive, setIsActive] = useState(false);
  const [isCreated, setIsCreated] = useState(true);

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Payment Verification',
      to: `/${businessArea}/payment-verification/`,
    },
  ];

  const toolbar = (
    <PageHeader
      title='Cash Plan (there should be ID)'
      breadCrumbs={breadCrumbsItems}
    >
      <>
        {!isActive && <NewPaymentVerificationDialog />}
        <Box display='flex'>
          {isCreated && <EditNewPaymentVerificationDialog />}
          <ActivateVerificationPlan />
        </Box>
        <FinishVerificationPlan />
        <DiscardVerificationPlan />
      </>
    </PageHeader>
  );

  return (
    <>
      {toolbar}
      <Container>
        <Grid container>
          <Grid item xs={9}>
            <Title>
              <Typography variant='h6'>
                {isActive ? 'Cash Plan ' : ''}Details
              </Typography>
            </Title>
            <Grid container>
              <Grid item xs={4}>
                <LabelizedField label='PROGRAMME NAME'>
                  <p>name</p>
                </LabelizedField>
              </Grid>
              <Grid item xs={4}>
                <LabelizedField label='PROGRAMME ID'>
                  <p>id</p>
                </LabelizedField>
              </Grid>
              <Grid item xs={4}>
                <LabelizedField label='PAYMENT RECORDS'>
                  <p>number of records</p>
                </LabelizedField>
              </Grid>
              <Grid item xs={4}>
                <LabelizedField label='START DATE'>
                  <p>some date</p>
                </LabelizedField>
              </Grid>
              <Grid item xs={4}>
                <LabelizedField label='END DATE'>
                  <p>some other date</p>
                </LabelizedField>
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={3}>
            <BorderLeftBox>
              <Title>
                <Typography variant='h6'>Bank reconciliation</Typography>
              </Title>
              <Grid container>
                <Grid item xs={6}>
                  <Grid container direction='column'>
                    <LabelizedField label='SUCCESSFUL'>
                      <p>90%</p>
                    </LabelizedField>
                    <LabelizedField label='ERRONEUS'>
                      <p>10%</p>
                    </LabelizedField>
                  </Grid>
                </Grid>
                <Grid item xs={6}>
                  <ChartContainer>
                    <Doughnut
                      width={100}
                      height={100}
                      options={{
                        maintainAspectRatio: false,
                        cutoutPercentage: 65,
                        legend: {
                          display: false,
                        },
                      }}
                      data={{
                        labels: ['Successful', 'Erroneus'],
                        datasets: [
                          {
                            data: [90, 10],
                            backgroundColor: ['#00509F', '#FFAA1F'],
                            hoverBackgroundColor: ['#00509F', '#FFAA1F'],
                          },
                        ],
                      }}
                    />
                  </ChartContainer>
                </Grid>
              </Grid>
            </BorderLeftBox>
          </Grid>
        </Grid>
      </Container>
      {isCreated && (
        <Container>
          <Title>
            <Typography variant='h6'>Verification Plan Details</Typography>
          </Title>
          <Grid container>
            <Grid item xs={9}>
              <Grid container>
                <Grid item xs={4}>
                  <LabelizedField label='STATUS'>
                    <p>S</p>
                  </LabelizedField>
                </Grid>
                <Grid item xs={4}>
                  <LabelizedField label='SAMPLE SIZE'>
                    <p>S</p>
                  </LabelizedField>
                </Grid>
                <Grid item xs={4}>
                  <LabelizedField label='RECEIVED'>
                    <p>S</p>
                  </LabelizedField>
                </Grid>
                <Grid item xs={4}>
                  <LabelizedField label='VERIFICATION METHOD'>
                    <p>S</p>
                  </LabelizedField>
                </Grid>
                <Grid item xs={4}>
                  <LabelizedField label='RESPONDED'>
                    <p>S</p>
                  </LabelizedField>
                </Grid>
                <Grid item xs={4}>
                  <LabelizedField label='NOT RECEIVED'>
                    <p>S</p>
                  </LabelizedField>
                </Grid>
                <Grid item xs={4}>
                  <LabelizedField label='SAMPLING'>
                    <p>S</p>
                  </LabelizedField>
                </Grid>
              </Grid>
            </Grid>
            <Grid item xs={3}>
              <Grid container>
                <Grid item xs={6}>
                  <Grid container direction='column'>
                    <LabelizedField label='RECEIVED CORRECT AMOUNT'>
                      <p>90%</p>
                    </LabelizedField>
                    <LabelizedField label='RECEIVED WRONG AMOUNT'>
                      <p>10%</p>
                    </LabelizedField>
                  </Grid>
                </Grid>
                <Grid item xs={6}>
                  <ChartContainer>
                    <Doughnut
                      width={100}
                      height={100}
                      options={{
                        maintainAspectRatio: false,
                        cutoutPercentage: 65,
                        legend: {
                          display: false,
                        },
                      }}
                      data={{
                        labels: ['CORRECT', 'WRONG'],
                        datasets: [
                          {
                            data: [90, 10],
                            backgroundColor: ['#74C304', '#DADADA'],
                            hoverBackgroundColor: ['#74C304', '#DADADA'],
                          },
                        ],
                      }}
                    />
                  </ChartContainer>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </Container>
      )}

      {!isActive && (
        <BottomTitle>
          To see more details please create Verification Plan
        </BottomTitle>
      )}

      <TableWrapper>
        <UniversalActivityLogTable objectId='some id' />
      </TableWrapper>
    </>
    //connect it later
  );
}
