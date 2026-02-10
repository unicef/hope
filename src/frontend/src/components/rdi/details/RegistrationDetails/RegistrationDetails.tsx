import { Box, Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { StatusBox } from '@core/StatusBox';
import { UniversalMoment } from '@core/UniversalMoment';
import { MiśTheme } from '../../../../theme';
import {
  formatFigure,
  registrationDataImportDeduplicationEngineStatusToColor,
  registrationDataImportStatusToColor,
} from '@utils/utils';
import { DedupeBox, OptionType } from '../DedupeBox';
import { Title } from '@core/Title';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { RegistrationDataImportStatusEnum } from '@restgenerated/models/RegistrationDataImportStatusEnum';
import { DeduplicationEngineStatusEnum } from '@restgenerated/models/DeduplicationEngineStatusEnum';

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
  registration: any;
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
                <BigValue>
                  {formatFigure(registration?.numberOfIndividuals)}
                </BigValue>
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
                <BigValue>
                  {formatFigure(registration?.numberOfHouseholds)}
                </BigValue>
              </LabelizedField>
            </BigValueContainer>
          </Grid>
          <Grid size={{ xs: 6 }}>
            <BigValueContainer>
              <LabelizedField
                label={`Total Number of ${beneficiaryGroup?.memberLabelPlural}`}
                dataCy="individuals"
              >
                <BigValue>
                  {formatFigure(registration?.numberOfIndividuals)}
                </BigValue>
              </LabelizedField>
            </BigValueContainer>
          </Grid>
        </Grid>
        <Grid container>
          <Grid size={{ xs: 6 }}>
            <Box mt={2}>
              <BigValueContainer>
                <LabelizedField
                  label={`${beneficiaryGroup?.memberLabelPlural} with records at HOPE`}
                  dataCy="registered-individuals"
                >
                  <BigValue>
                    {formatFigure(registration?.numberOfRegisteredIndividuals)}
                  </BigValue>
                </LabelizedField>
              </BigValueContainer>
            </Box>
          </Grid>
        </Grid>
      </Grid>
    );
  }
  const showBiographicalDeduplicationResult =
    registration.status !== RegistrationDataImportStatusEnum.DEDUPLICATION;
  const showBiometricDeduplicationResult =
    registration.biometricDeduplicationEnabled &&
    registration.deduplicationEngineStatus ===
      DeduplicationEngineStatusEnum.FINISHED;
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
                  value={registration?.importedBy}
                />
              </Grid>
              {registration.status === 'REFUSED' &&
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
          {registration.status ===
            RegistrationDataImportStatusEnum.DEDUPLICATION_FAILED ||
          (!showBiographicalDeduplicationResult &&
            !showBiometricDeduplicationResult) ? null : (
            <Grid size={{ xs: 'auto' }}>
              <Grid container direction="column">
                <Grid container size={{ xs: 12 }} spacing={3}>
                  <Grid size={{ xs: 4 }}></Grid>
                  {showBiographicalDeduplicationResult && (
                    <Grid size={{ xs: 4 }}>
                      <BoldGrey>{t('Biographical')}</BoldGrey>
                    </Grid>
                  )}
                  {showBiometricDeduplicationResult && (
                    <Grid size={{ xs: 4 }}>
                      <BoldGrey>{t('Biometrics')}</BoldGrey>
                    </Grid>
                  )}
                </Grid>
                <DedupeBox
                  showBiographicalDeduplicationResult={
                    showBiographicalDeduplicationResult
                  }
                  showBiometricDeduplicationResult={
                    showBiometricDeduplicationResult
                  }
                  label="Within Batch"
                  options={withinBatchOptions}
                />
                <DedupeBox
                  showBiographicalDeduplicationResult={
                    showBiographicalDeduplicationResult
                  }
                  showBiometricDeduplicationResult={
                    showBiometricDeduplicationResult
                  }
                  label="In Population"
                  options={populationOptions}
                />
              </Grid>
            </Grid>
          )}
        </Grid>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
}

export default withErrorBoundary(RegistrationDetails, 'RegistrationDetails');
