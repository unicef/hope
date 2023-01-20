import { Grid, Typography } from '@material-ui/core';
import { Title } from '@material-ui/icons';
import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  enrollmentStatusToColor,
  renderUserName,
  targetPopulationStatusMapping,
} from '../../../utils/utils';
import { TargetPopulationQuery } from '../../../__generated__/graphql';
import { ContainerColumnWithBorder } from '../../core/ContainerColumnWithBorder';
import { LabelizedField } from '../../core/LabelizedField';
import { OverviewContainer } from '../../core/OverviewContainer';
import { StatusBox } from '../../core/StatusBox';
import { UniversalMoment } from '../../core/UniversalMoment';

interface EnrollmentDetailsProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
}

export const EnrollmentDetails = ({
  targetPopulation,
}: EnrollmentDetailsProps): React.ReactElement => {
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
    <ContainerColumnWithBorder data-cy='enrollment-details-container'>
      <Title>
        <Typography variant='h6'>{t('Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField
              label={t('created by')}
              value={renderUserName(createdBy)}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label={t('Program population close date')}
              value={closeDate}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label={t('Program')} value={programName} />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label={t('Send by')} value={sendBy} />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label={t('Send date')} value={sendDate} />
          </Grid>
        </Grid>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
};
