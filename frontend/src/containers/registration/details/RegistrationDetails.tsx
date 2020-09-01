import React from 'react';
import styled from 'styled-components';
import { Grid, Typography, Box } from '@material-ui/core';
import { StatusBox } from '../../../components/StatusBox';
import { registrationDataImportStatusToColor } from '../../../utils/utils';
import { LabelizedField } from '../../../components/LabelizedField';
import { RegistrationDetailedFragment } from '../../../__generated__/graphql';
import { MiśTheme } from '../../../theme';

const Container = styled.div`
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
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
  min-width: 120px;
  max-width: 200px;
`;

const BigValueContainer = styled.div`
  padding: ${({ theme }) => theme.spacing(6)}px;
  border-color: #b1b1b5;
  border-left-width: 1px;
  border-left-style: solid;
  display: flex;
  height: 180px;
`;
const BigValue = styled.div`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 36px;
  line-height: 32px;
  margin-top: ${({ theme }) => theme.spacing(2)}px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const Bold = styled.span`
  font-weight: bold;
  font-size: 16px;
`;

const BoldGrey = styled.span`
  font-weight: bold;
  font-size: 16px
  color: rgba(37, 59, 70, 0.6);
`;

const Error = styled.p`
  color: ${({ theme }: { theme: MiśTheme }) => theme.hctPalette.red};
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
        <Typography variant='h6'>Import Details</Typography>
      </Title>
      <OverviewContainer>
        <Grid alignItems='center' container spacing={3}>
          <Grid item xs={2}>
            <Box display='flex' flexDirection='column'>
              <LabelizedField label='status'>
                <StatusContainer>
                  <StatusBox
                    status={registration.status}
                    statusToColor={registrationDataImportStatusToColor}
                  />
                </StatusContainer>
              </LabelizedField>
              {registration.errorMessage && (
                <Error>{registration.errorMessage}</Error>
              )}
            </Box>
          </Grid>
          <Grid item xs={1}>
            <LabelizedField
              label='Source of Data'
              value={registration.dataSource}
            />
          </Grid>
          <Grid item xs={2}>
            <BigValueContainer>
              <LabelizedField
                label='Total Number of Households'
                dataCy='households'
              >
                <BigValue>{registration.numberOfHouseholds}</BigValue>
              </LabelizedField>
            </BigValueContainer>
          </Grid>
          <Grid item xs={2}>
            <BigValueContainer>
              <LabelizedField
                label='Total Number of Individuals'
                dataCy='individuals'
              >
                <BigValue>{registration.numberOfIndividuals}</BigValue>
              </LabelizedField>
            </BigValueContainer>
          </Grid>
          <Grid item xs={2}>
            <BigValueContainer>
              <LabelizedField label='Dedupe within batch'>
                <div>
                  <p>
                    <Bold>78%</Bold> <BoldGrey>(104)</BoldGrey> Unique
                  </p>
                  <p>
                    <Bold>28%</Bold> <BoldGrey>(24)</BoldGrey> Duplicates
                  </p>
                </div>
              </LabelizedField>
            </BigValueContainer>
          </Grid>
          <Grid item xs={3}>
            <BigValueContainer>
              <LabelizedField label='Dedupe against population'>
                <div>
                  <p>
                    <Bold>78% </Bold>
                    <BoldGrey>(104)</BoldGrey> Unique
                  </p>
                  <p>
                    <Bold>28%</Bold>
                    <BoldGrey> (24)</BoldGrey> Duplicates
                  </p>
                  <p>
                    <Bold>11%</Bold> <BoldGrey>(11)</BoldGrey> Need Adjudication
                  </p>
                </div>
              </LabelizedField>
            </BigValueContainer>
          </Grid>
        </Grid>
      </OverviewContainer>
    </Container>
  );
}
