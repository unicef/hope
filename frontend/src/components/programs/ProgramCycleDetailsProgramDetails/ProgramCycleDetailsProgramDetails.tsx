import { Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ProgramCycleQuery } from '../../../__generated__/graphql';
import { programCycleStatusToColor } from '../../../utils/utils';
import { ContainerColumnWithBorder } from '../../core/ContainerColumnWithBorder';
import { LabelizedField } from '../../core/LabelizedField';
import { Missing } from '../../core/Missing';
import { OverviewContainer } from '../../core/OverviewContainer';
import { StatusBox } from '../../core/StatusBox';
import { Title } from '../../core/Title';
import { UniversalMoment } from '../../core/UniversalMoment';

interface ProgramCycleDetailsProgramDetailsProps {
  programCycle: ProgramCycleQuery['programCycle'];
  statusChoices: {
    [id: number]: string;
  };
}

export const ProgramCycleDetailsProgramDetails = ({
  programCycle,
  statusChoices,
}: ProgramCycleDetailsProgramDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  //TODO: add created by, frequency of payment
  const {
    status,
    startDate,
    endDate,
    program: { startDate: programStartDate, endDate: programEndDate },
  } = programCycle;
  return (
    <Grid item xs={12}>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>{t('Details')}</Typography>
        </Title>
        <OverviewContainer>
          <Grid container spacing={6}>
            <Grid item xs={12}>
              <StatusBox
                status={statusChoices[status]}
                statusToColor={programCycleStatusToColor}
              />
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Created By')}>
                <Missing />
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Start Date')}>
                <UniversalMoment>{startDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('End Date')}>
                <UniversalMoment>{endDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Programme Start Date')}>
                <UniversalMoment>{programStartDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Programme End Date')}>
                <UniversalMoment>{programEndDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Frequency of Payment')}>
                <Missing />
              </LabelizedField>
            </Grid>
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
};
