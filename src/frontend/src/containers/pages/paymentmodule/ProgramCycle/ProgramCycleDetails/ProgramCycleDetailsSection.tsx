import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { StatusBox } from '@core/StatusBox';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { Grid, Typography } from '@mui/material';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { programCycleStatusToColor } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

interface ProgramCycleDetailsSectionProps {
  programCycle: ProgramCycleList;
}

export const ProgramCycleDetailsSection = ({
  programCycle,
}: ProgramCycleDetailsSectionProps): ReactElement => {
  const { t } = useTranslation();
  return (
    <Grid size={12}>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant="h6">{t('Details')}</Typography>
        </Title>
        <OverviewContainer>
          <Grid container spacing={6}>
            <Grid size={12}>
              <StatusBox
                status={programCycle.status}
                statusToColor={programCycleStatusToColor}
              />
            </Grid>
            <Grid size={3}>
              <LabelizedField label={t('Created By')}>
                {programCycle.createdBy}
              </LabelizedField>
            </Grid>
            <Grid size={3}>
              <LabelizedField label={t('Start Date')}>
                <UniversalMoment>{programCycle.startDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={3}>
              <LabelizedField label={t('End Date')}>
                <UniversalMoment>{programCycle.endDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={3}>
              <LabelizedField label={t('Programme Start Date')}>
                <UniversalMoment>
                  {programCycle.programStartDate}
                </UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={3}>
              <LabelizedField label={t('Programme End Date')}>
                <UniversalMoment>{programCycle.programEndDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={3}>
              <LabelizedField label={t('Frequency of Payment')}>
                {programCycle.frequencyOfPayments}
              </LabelizedField>
            </Grid>
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
};
