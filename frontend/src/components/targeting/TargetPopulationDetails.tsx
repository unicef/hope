import { Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { targetPopulationStatusToColor } from '../../utils/utils';
import { TargetPopulationQuery } from '../../__generated__/graphql';
import { ContainerColumnWithBorder } from '../core/ContainerColumnWithBorder';
import { LabelizedField } from '../core/LabelizedField';
import { OverviewContainer } from '../core/OverviewContainer';
import { StatusBox } from '../core/StatusBox';
import { Title } from '../core/Title';
import { UniversalMoment } from '../core/UniversalMoment';

interface ProgramDetailsProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
}

export function TargetPopulationDetails({
  targetPopulation,
}: ProgramDetailsProps): React.ReactElement {
  const {
    createdBy,
    finalizedBy,
    changeDate,
    finalizedAt,
    program,
  } = targetPopulation;
  const { t } = useTranslation();
  const closeDate = changeDate ? (
    <UniversalMoment>{changeDate}</UniversalMoment>
  ) : (
    '-'
  );
  const sendBy = finalizedBy
    ? `${finalizedBy.firstName} ${finalizedBy.lastName}`
    : '-';
  const sendDate = finalizedAt ? (
    <UniversalMoment>{finalizedAt}</UniversalMoment>
  ) : (
    '-'
  );
  const programName = program?.name ? program.name : '-';
  return (
    <ContainerColumnWithBorder data-cy='target-population-details-container'>
      <Title data-cy='details-title'>
        <Typography variant='h6'>{t('Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid data-cy='details-grid' container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField label={t('Status')}>
              <StatusBox
                dataCy='target-population-status'
                status={targetPopulation.status}
                statusToColor={targetPopulationStatusToColor}
              />
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              dataCy='created-by'
              label={t('created by')}
              value={`${createdBy.firstName} ${createdBy.lastName}`}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              dataCy='close-date'
              label={t('Programme population close date')}
              value={closeDate}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              dataCy='program-name'
              label={t('Programme')}
              value={programName}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              dataCy='send-by'
              label={t('Send by')}
              value={sendBy}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              dataCy='send-date'
              label={t('Send date')}
              value={sendDate}
            />
          </Grid>
        </Grid>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
}
