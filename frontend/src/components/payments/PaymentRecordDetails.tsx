import React from 'react';
import styled from 'styled-components';
import { Grid, Paper, Typography } from '@material-ui/core';
import moment from 'moment';
import { StatusBox } from '../StatusBox';
import { programStatusToColor } from '../../utils/utils';
import { LabelizedField } from '../LabelizedField';
import { PaymentRecordNode, ProgramNode } from '../../__generated__/graphql';
import { MiśTheme } from '../../theme';

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
const OverviewContainer = styled.div`
  display: flex;
  align-items: center;
  flex-direction: row;
`;

const StatusContainer = styled.div`
  width: 120px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const OverviewGrid = styled(Grid)`
  max-width: 1000px;
`;
const PageContainer = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: ${({ theme }) => theme.spacing(5)}px;
`;

const Card = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(6)}px;
`;

const HouseholdDataContainer = styled.div`
  margin-top: ${({ theme }) => theme.spacing(2)}px;
`;
const LabelizedFieldContainer = styled.div`
  margin-top: ${({ theme }) => theme.spacing(6)}px;
`;
const EntitlementDataContainer = styled.div`
  margin-top: ${({ theme }) => theme.spacing(6)}px;
`;

interface PaymentRecordDetailsProps {
  paymentRecord: PaymentRecordNode;
}

export function PaymentRecordDetails({
  paymentRecord,
}: PaymentRecordDetailsProps): React.ReactElement {
  return (
    <>
      <Container>
        <Title>
          <Typography variant='h6'>Payment Record Details</Typography>
        </Title>
        <OverviewContainer>
          <OverviewGrid container spacing={6}>
            <Grid item xs={4}>
              <LabelizedField label='status'>
                <StatusContainer>
                  <StatusBox
                    status='COMPLETE'
                    statusToColor={programStatusToColor}
                  />
                </StatusContainer>
              </LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label='Registration Group' value='183-19-13723' />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label='Distribution Modality' value='183-31' />
            </Grid>

            <Grid item xs={4}>
              <LabelizedField label='Business Unit' value='Greece - CO' />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField
                label='Target Population'
                value='GDT Greece Groups'
              />
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label='Comments' value='TEST TEST TEST TEST' />
            </Grid>
          </OverviewGrid>
        </OverviewContainer>
      </Container>

      <PageContainer>
        <Grid container spacing={5}>
          <Grid item xs={4}>
            <Card>
              <Typography variant='h6'>Household</Typography>
              <HouseholdDataContainer>
                <LabelizedFieldContainer>
                  <LabelizedField
                    label='household id'
                    value={paymentRecord.household.householdCaId}
                  />
                </LabelizedFieldContainer>
                <LabelizedFieldContainer>
                  <LabelizedField
                    label='head of household'
                    value='Jan Romaniak'
                  />
                </LabelizedFieldContainer>
                <LabelizedFieldContainer>
                  <LabelizedField label='total person covered' value='4' />
                </LabelizedFieldContainer>
              </HouseholdDataContainer>
            </Card>
          </Grid>

          <Grid item xs={8}>
            <Card>
              <Typography variant='h6'>Entitlement Details</Typography>
              <EntitlementDataContainer>
                <Grid container spacing={6}>
                  <Grid item xs={4}>
                    <LabelizedField
                      label='Entitlement quantity'
                      value='20.00'
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <LabelizedField label='Currency' value='Idian Ruple' />
                  </Grid>
                  <Grid item xs={4}>
                    <LabelizedField
                      label='Delivery type'
                      value={paymentRecord.deliveryType}
                    />
                  </Grid>

                  <Grid item xs={4}>
                    <LabelizedField label='Delivered quantity' value='20.00' />
                  </Grid>
                  <Grid item xs={4}>
                    <LabelizedField label='Delivery date' value='14 Oct 2019' />
                  </Grid>
                  <Grid item xs={4} />

                  <Grid item xs={4}>
                    <LabelizedField
                      label='Entitlement Card Status'
                      value='Active'
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <LabelizedField
                      label='Entitlement Card Issue Date'
                      value='14 Oct 2019'
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <LabelizedField label='FSP' value='14 Oct 2019' />
                  </Grid>
                </Grid>
              </EntitlementDataContainer>
            </Card>
          </Grid>
        </Grid>
      </PageContainer>
    </>
  );
}
