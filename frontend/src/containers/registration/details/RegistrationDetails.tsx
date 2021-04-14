import React from 'react';
import styled from 'styled-components';
import { Grid, Typography, Box } from '@material-ui/core';
import { StatusBox } from '../../../components/StatusBox';
import { registrationDataImportStatusToColor } from '../../../utils/utils';
import { LabelizedField } from '../../../components/LabelizedField';
import { UniversalMoment } from '../../../components/UniversalMoment';
import { RegistrationDetailedFragment } from '../../../__generated__/graphql';
import { MiśTheme } from '../../../theme';
import { ContainerColumnWithBorder } from '../../../components/ContainerColumnWithBorder';
import { OverviewContainer } from '../../../components/OverviewContainer';
import { DedupeBox } from './DedupeBox';

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
`;
const BigValue = styled.div`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 36px;
  line-height: 32px;
  margin-top: ${({ theme }) => theme.spacing(2)}px;
`;

const Error = styled.p`
  color: ${({ theme }: { theme: MiśTheme }) => theme.hctPalette.red};
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
  const withinBatchOptions = [
    {
      name: 'Unique',
      percent: registration?.batchUniqueCountAndPercentage.percentage,
      value: registration?.batchUniqueCountAndPercentage.count,
    },
    {
      name: 'Duplicates',
      percent: registration?.batchDuplicatesCountAndPercentage.percentage,
      value: registration?.batchDuplicatesCountAndPercentage.count,
    },
  ];
  const populationOptions = [
    {
      name: 'Unique',
      percent: registration?.goldenRecordUniqueCountAndPercentage.percentage,
      value: registration?.goldenRecordUniqueCountAndPercentage.count,
    },
    {
      name: 'Duplicates',
      percent:
        registration?.goldenRecordDuplicatesCountAndPercentage.percentage,
      value: registration?.goldenRecordDuplicatesCountAndPercentage.count,
    },
    {
      name: 'Need Adjudication',
      percent:
        registration?.goldenRecordPossibleDuplicatesCountAndPercentage
          .percentage,
      value:
        registration?.goldenRecordPossibleDuplicatesCountAndPercentage.count,
    },
  ];
  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant='h6'>Import Details</Typography>
      </Title>
      <OverviewContainer>
        <Grid alignItems='center' container>
          <Grid item xs={4}>
            <Grid container spacing={3}>
              <Grid item xs={6}>
                <Box display='flex' flexDirection='column'>
                  <LabelizedField label='status'>
                    <StatusContainer>
                      <StatusBox
                        status={registration?.status}
                        statusToColor={registrationDataImportStatusToColor}
                      />
                    </StatusContainer>
                  </LabelizedField>
                  {registration?.errorMessage && (
                    <Error>{registration.errorMessage}</Error>
                  )}
                </Box>
              </Grid>
              <Grid item xs={6}>
                <LabelizedField
                  label='Source of Data'
                  value={registration?.dataSource}
                />
              </Grid>
              <Grid item xs={6}>
                <LabelizedField
                  label='Import Date'
                  value={
                    <UniversalMoment withTime>
                      {registration?.importDate}
                    </UniversalMoment>
                  }
                />
              </Grid>
              <Grid item xs={6}>
                <LabelizedField
                  label='Imported by'
                  value={`${registration?.importedBy?.firstName} ${registration?.importedBy?.lastName}`}
                />
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={4}>
            <Grid container>
              <Grid item xs={6}>
                <BigValueContainer>
                  <LabelizedField
                    label='Total Number of Households'
                    dataCy='households'
                  >
                    <BigValue>{registration?.numberOfHouseholds}</BigValue>
                  </LabelizedField>
                </BigValueContainer>
              </Grid>
              <Grid item xs={6}>
                <BigValueContainer>
                  <LabelizedField
                    label='Total Number of Individuals'
                    dataCy='individuals'
                  >
                    <BigValue>{registration?.numberOfIndividuals}</BigValue>
                  </LabelizedField>
                </BigValueContainer>
              </Grid>
            </Grid>
          </Grid>
          {registration.status === 'DEDUPLICATION_FAILED' ? null : (
            <Grid item xs={4}>
              <Grid container direction='column'>
                <DedupeBox label='Within Batch' options={withinBatchOptions} />
                <DedupeBox label='In Population' options={populationOptions} />
              </Grid>
            </Grid>
          )}
        </Grid>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
}
