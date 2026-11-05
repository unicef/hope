import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { StatusBox } from '@core/StatusBox';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { Grid, Typography } from '@mui/material';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';
import type { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { programCycleStatusToColor } from '@utils/utils';
import type { ReactElement } from 'react';
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
          <ResponsiveGridContainer spacing={6}>
            <ResponsiveGrid size="full">
              <StatusBox
                status={programCycle.status}
                statusToColor={programCycleStatusToColor}
              />
            </ResponsiveGrid>
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField label={t('Created By')}>
                {programCycle.createdBy}
              </LabelizedField>
            </ResponsiveGrid>
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField label={t('Start Date')}>
                <UniversalMoment>{programCycle.startDate}</UniversalMoment>
              </LabelizedField>
            </ResponsiveGrid>
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField label={t('End Date')}>
                <UniversalMoment>{programCycle.endDate}</UniversalMoment>
              </LabelizedField>
            </ResponsiveGrid>
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField label={t('Programme Start Date')}>
                <UniversalMoment>
                  {programCycle.programStartDate}
                </UniversalMoment>
              </LabelizedField>
            </ResponsiveGrid>
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField label={t('Programme End Date')}>
                <UniversalMoment>{programCycle.programEndDate}</UniversalMoment>
              </LabelizedField>
            </ResponsiveGrid>
            <ResponsiveGrid size="quarter" mobileSize="half">
              <LabelizedField label={t('Frequency of Payment')}>
                {programCycle.frequencyOfPayments}
              </LabelizedField>
            </ResponsiveGrid>
          </ResponsiveGridContainer>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
};
