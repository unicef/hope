import React from 'react';
import styled from 'styled-components';
import { Grid, Typography } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';
import { TargetPopulationNode } from '../../__generated__/graphql';
import { UniversalMoment } from '../UniversalMoment';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { OverviewContainer } from '../OverviewContainer';

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
        <Typography variant='h6'>Details</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            <LabelizedField
              label='created by'
              value={`${createdBy.firstName} ${createdBy.lastName}`}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='Programme population close date'
              value={closeDate}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Programme' value={programName} />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Send by' value={sendBy} />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Send date' value={sendDate} />
          </Grid>
        </Grid>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
}
