import React, { ReactElement } from 'react';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { Title } from '@core/Title';
import { Typography } from '@mui/material';
import { OverviewContainer } from '@core/OverviewContainer';
import Grid from '@mui/material/Grid2';
import { StatusBox } from '@core/StatusBox';
import { programCycleStatusToColor } from '@utils/utils';
import { LabelizedField } from '@core/LabelizedField';
import { UniversalMoment } from '@core/UniversalMoment';
import { ProgramCycle } from '@api/programCycleApi';
import { useTranslation } from 'react-i18next';

interface ProgramCycleDetailsSectionProps {
  programCycle: ProgramCycle;
}

export const ProgramCycleDetailsSection = ({
  programCycle,
}: ProgramCycleDetailsSectionProps): ReactElement => {
  const { t } = useTranslation();
  return (
    <Grid size={{ xs: 12 }}>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">{t('Details')}</Typography>
        </Title>
        <OverviewContainer>
          <Grid container spacing={6}>
            <Grid size={{ xs: 12 }}>
              <StatusBox
                status={programCycle.status}
                statusToColor={programCycleStatusToColor}
              />
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Created By')}>
                {programCycle.created_by}
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Start Date')}>
                <UniversalMoment>{programCycle.start_date}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('End Date')}>
                <UniversalMoment>{programCycle.end_date}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Programme Start Date')}>
                <UniversalMoment>
                  {programCycle.program_start_date}
                </UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Programme End Date')}>
                <UniversalMoment>
                  {programCycle.program_end_date}
                </UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Frequency of Payment')}>
                {programCycle.frequency_of_payments}
              </LabelizedField>
            </Grid>
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
};
