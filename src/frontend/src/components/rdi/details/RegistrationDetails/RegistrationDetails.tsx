import { Box, Grid2 as Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { StatusBox } from '@core/StatusBox';
import { UniversalMoment } from '@core/UniversalMoment';
import { MiśTheme } from '../../../../theme';
import {
  registrationDataImportDeduplicationEngineStatusToColor,
  registrationDataImportStatusToColor,
} from '@utils/utils';
import {
  RegistrationDataImportQuery,
  RegistrationDataImportStatus,
} from '@generated/graphql';
import { DedupeBox, OptionType } from '../DedupeBox';
import { Title } from '@core/Title';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

export const BigValueContainer = styled.div`
  padding: ${({ theme }) => theme.spacing(6)};
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
  margin-top: ${({ theme }) => theme.spacing(2)};
`;

const Error = styled.p`
  color: ${({ theme }: { theme: MiśTheme }) => theme.hctPalette.red};
  font-size: 12px;
`;

const BoldGrey = styled.span`
  font-weight: bold;
  font-size: 14px;
  color: rgba(37, 59, 70, 0.6);
`;

interface RegistrationDetailsProps {
  registration: RegistrationDataImportQuery['registrationDataImport'];
  isSocialWorkerProgram?: boolean;
}

function RegistrationDetails({
  registration,
  isSocialWorkerProgram,
}: RegistrationDetailsProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const withinBatchOptions: OptionType[] = [
    {
      name: 'Unique',
      options: registration?.batchUniqueCountAndPercentage,
    },
    {
      name: 'Duplicates',
      options: registration?.batchDuplicatesCountAndPercentage,
    },
  ];
  const populationOptions: OptionType[] = [
    {
      name: 'Unique',
      options: registration?.goldenRecordUniqueCountAndPercentage,
    },
    {
      name: 'Duplicates',
      options: registration?.goldenRecordDuplicatesCountAndPercentage,
    },
    {
      name: 'Need Adjudication',
      options: registration?.goldenRecordPossibleDuplicatesCountAndPercentage,
    },
  ];
  const renderImportedBy = (): string => {
    if (registration?.importedBy) {
      return `${registration?.importedBy?.firstName} ${registration?.importedBy?.lastName}`;
    }
    return '-';
  };

  let numbersComponent: ReactElement;
  if (isSocialWorkerProgram) {
    numbersComponent = (
      <Grid size={{ xs: 4 }}>
        <Grid container>
          <Grid size={{ xs: 6 }}>
            <BigValueContainer>
              <LabelizedField
                label={t('Total Number of Registered People')}
                dataCy="individuals"
              >
                <BigValue>{registration?.numberOfIndividuals}</BigValue>
              </LabelizedField>
            </BigValueContainer>
          </Grid>
        </Grid>
      </Grid>
    );
  } else {
    numbersComponent = (
      <Grid size={{ xs: 'auto' }}>
        <Grid container>
          <Grid size={{ xs: 6 }}>
            <BigValueContainer>
              <LabelizedField
                label={`Total Number of ${beneficiaryGroup?.groupLabelPlural}`}
                dataCy="households"
              >
                <BigValue>{registration?.numberOfHouseholds}</BigValue>
              </LabelizedField>
            </BigValueContainer>
          </Grid>
          <Grid size={{ xs: 6 }}>
            <BigValueContainer>
              <LabelizedField
                label={`Total Number of ${beneficiaryGroup?.memberLabelPlural}`}
                dataCy="individuals"
              >
                <BigValue>{registration?.numberOfIndividuals}</BigValue>
              </LabelizedField>
            </BigValueContainer>
          </Grid>
        </Grid>
      </Grid>
    );
  }
  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant="h6">{t('Import Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid alignItems="center" container>
          <Grid size={{ xs: 'auto' }}>
            <Grid container spacing={3}>
              <Grid size={{ xs: 6 }}>
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
              {registration?.biometricDeduplicationEnabled && (
                <Grid size={{ xs: 6 }}>
                  <Box display="flex" flexDirection="column">
                    <LabelizedField
                      label={t('Biometrics Deduplication Status')}
                    >
                      <StatusBox
                        status={registration?.deduplicationEngineStatus}
                        statusToColor={
                          registrationDataImportDeduplicationEngineStatusToColor
                        }
                      />
                    </LabelizedField>
                    {registration?.errorMessage && (
                      <Error>{registration.errorMessage}</Error>
                    )}
                  </Box>
                </Grid>
              )}
              <Grid size={{ xs: 6 }}>
                <LabelizedField
                  label={t('Source of Data')}
                  value={registration?.dataSource}
                />
              </Grid>
              <Grid size={{ xs: 6 }}>
                <LabelizedField
                  label={t('Import Date')}
                  value={
                    <UniversalMoment withTime>
                      {registration?.importDate}
                    </UniversalMoment>
                  }
                />
              </Grid>
              <Grid size={{ xs: 6 }}>
                <LabelizedField
                  label={t('Imported by')}
                  value={renderImportedBy()}
                />
              </Grid>
              {registration.status === RegistrationDataImportStatus.Refused &&
              registration.refuseReason ? (
                <Grid size={{ xs: 6 }}>
                  <LabelizedField
                    label={t('Refuse Reason')}
                    value={registration?.refuseReason}
                  />
                </Grid>
              ) : null}
            </Grid>
          </Grid>
          {numbersComponent}
          {registration.status === 'DEDUPLICATION_FAILED' ? null : (
            <Grid size={{ xs: 'auto' }}>
              <Grid container direction="column">
                <Grid container size={{ xs: 12 }} spacing={3}>
                  <Grid size={{ xs: 4 }}></Grid>
                  <Grid size={{ xs: 4 }}>
                    <BoldGrey>{t('Biographical')}</BoldGrey>
                  </Grid>
                  {registration.biometricDeduplicationEnabled && (
                    <Grid size={{ xs: 4 }}>
                      <BoldGrey>{t('Biometrics')}</BoldGrey>
                    </Grid>
                  )}
                </Grid>
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

export default withErrorBoundary(RegistrationDetails, 'RegistrationDetails');
