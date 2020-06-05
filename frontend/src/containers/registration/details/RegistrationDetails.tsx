import React from 'react';
import styled from 'styled-components';
import { Grid, Typography } from '@material-ui/core';
import { Doughnut } from 'react-chartjs-2';
import { StatusBox } from '../../../components/StatusBox';
import { registrationDataImportStatusToColor } from '../../../utils/utils';
import { LabelizedField } from '../../../components/LabelizedField';
import { RegistrationDetailedFragment } from '../../../__generated__/graphql';
import { MiśTheme } from '../../../theme';

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

const BigValueContainer = styled.div`
  padding: ${({ theme }) => theme.spacing(6)}px;
  border-color: #b1b1b5;
  border-left-width: 1px;
  border-left-style: solid;
  display: flex;
  align-items: flex-end;
  height: 120px;
`;
const BigValue = styled.div`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 36px;
  line-height: 32px;
  margin-top: ${({ theme }) => theme.spacing(2)}px;
`;
const ChartContainer = styled.div`
  width: 100px;
  height: 100px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface RegistrationDetailsProps {
  registration: RegistrationDetailedFragment;
}

export function RegistrationDetails({
  registration,
}: RegistrationDetailsProps): React.ReactElement {
  return (
    <Container>
      <Title>
        <Typography variant='h6'>Import Data Details</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField label='status'>
              <StatusContainer>
                <StatusBox
                  status={registration.status}
                  statusToColor={registrationDataImportStatusToColor}
                />
              </StatusContainer>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='DATA SOURCE'
              value={registration.dataSource}
            />
          </Grid>
        </Grid>
        <BigValueContainer>
          <LabelizedField
            label='Total Number of Households'
            dataCy='households'
          >
            <BigValue>{registration.numberOfHouseholds}</BigValue>
          </LabelizedField>
        </BigValueContainer>
        <BigValueContainer>
          <LabelizedField
            label='Total Number of Individuals'
            dataCy='individuals'
          >
            <BigValue>{registration.numberOfIndividuals}</BigValue>
          </LabelizedField>
        </BigValueContainer>
        <BigValueContainer>
          <LabelizedField label='Correct'>
            <BigValue>90%</BigValue>
          </LabelizedField>
        </BigValueContainer>
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
              labels: ['Correct', 'Not Correct'],
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
      </OverviewContainer>
    </Container>
  );
}
