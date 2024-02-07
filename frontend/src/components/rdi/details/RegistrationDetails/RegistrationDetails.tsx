import { Box, Grid, Typography } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { LabelizedField } from '../../../core/LabelizedField';
import { OverviewContainer } from '../../../core/OverviewContainer';
import { StatusBox } from '../../../core/StatusBox';
import { UniversalMoment } from '../../../core/UniversalMoment';
import { MiśTheme } from '../../../../theme';
import { registrationDataImportStatusToColor } from '@utils/utils';
import {
  RegistrationDetailedFragment,
  RegistrationDataImportStatus,
} from '../../../../__generated__/graphql';
import { DedupeBox } from '../DedupeBox';
import { Title } from '../../../core/Title';

export const BigValueContainer = styled.div`
  padding: ${({ theme }) => theme.spacing(6)}px;
  border-color: #b1b1b5;
  border-left-width: 1px;
  border-left-style: solid;
  display: flex;
`;
export const BigValue = styled.div`
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
interface RegistrationDetailsProps {
  registration: RegistrationDetailedFragment;
}

export function RegistrationDetails({
  registration,
}: RegistrationDetailsProps): React.ReactElement {
  const { t } = useTranslation();
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
  const renderImportedBy = (): string => {
    if (registration?.importedBy) {
      return `${registration?.importedBy?.firstName} ${registration?.importedBy?.lastName}`;
    }
    return '-';
  };
  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant="h6">{t('Import Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid alignItems="center" container>
          <Grid item xs={4}>
            <Grid container spacing={3}>
              <Grid item xs={6}>
                <Box display="flex" flexDirection="column">
                  <LabelizedField label={t('status')}>
                    <StatusBox
                      status={registration?.status}
                      statusToColor={registrationDataImportStatusToColor}
                    />
                  </LabelizedField>
                  {registration?.errorMessage && (
                    <Error>{registration.errorMessage}</Error>
                  )}
                </Box>
              </Grid>
              <Grid item xs={6}>
                <LabelizedField
                  label={t('Source of Data')}
                  value={registration?.dataSource}
                />
              </Grid>
              <Grid item xs={6}>
                <LabelizedField
                  label={t('Import Date')}
                  value={
                    <UniversalMoment withTime>
                      {registration?.importDate}
                    </UniversalMoment>
                  }
                />
              </Grid>
              <Grid item xs={6}>
                <LabelizedField
                  label={t('Imported by')}
                  value={renderImportedBy()}
                />
              </Grid>
              {registration.status === RegistrationDataImportStatus.Refused &&
              registration.refuseReason ? (
                <Grid item xs={6}>
                  <LabelizedField
                    label={t('Refuse Reason')}
                    value={registration?.refuseReason}
                  />
                </Grid>
              ) : null}
            </Grid>
          </Grid>
          <Grid item xs={4}>
            <Grid container>
              <Grid item xs={6}>
                <BigValueContainer>
                  <LabelizedField
                    label={t('Total Number of Households')}
                    dataCy="households"
                  >
                    <BigValue>{registration?.numberOfHouseholds}</BigValue>
                  </LabelizedField>
                </BigValueContainer>
              </Grid>
              <Grid item xs={6}>
                <BigValueContainer>
                  <LabelizedField
                    label={t('Total Number of Individuals')}
                    dataCy="individuals"
                  >
                    <BigValue>{registration?.numberOfIndividuals}</BigValue>
                  </LabelizedField>
                </BigValueContainer>
              </Grid>
            </Grid>
          </Grid>
          {registration.status === 'DEDUPLICATION_FAILED' ? null : (
            <Grid item xs={4}>
              <Grid container direction="column">
                <DedupeBox label="Within Batch" options={withinBatchOptions} />
                <DedupeBox label="In Population" options={populationOptions} />
              </Grid>
            </Grid>
          )}
        </Grid>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
}
