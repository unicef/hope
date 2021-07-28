import { Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { TargetPopulationNode } from '../../__generated__/graphql';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { LabelizedField } from '../LabelizedField';
import { OverviewContainer } from '../OverviewContainer';
import { UniversalMoment } from '../UniversalMoment';

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface ProgramDetailsProps {
  targetPopulation: TargetPopulationNode;
}

export function TargetPopulationDetails({
  targetPopulation,
}: ProgramDetailsProps): React.ReactElement {
  const {
    createdBy,
    finalizedBy,
    approvedAt,
    finalizedAt,
    program,
  } = targetPopulation;
  const { t } = useTranslation();
  const closeDate = approvedAt ? (
    <UniversalMoment>{approvedAt}</UniversalMoment>
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
      <Title>
        <Typography variant='h6'>{t('Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField
              label={t('created by')}
              value={`${createdBy.firstName} ${createdBy.lastName}`}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label={t('Programme population close date')}
              value={closeDate}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label={t('Programme')} value={programName} />
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
}
