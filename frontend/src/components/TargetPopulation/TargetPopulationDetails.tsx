import React from 'react';
import styled from 'styled-components';
import { Grid, Typography } from '@material-ui/core';
import moment from 'moment';
import { LabelizedField } from '../LabelizedField';
import {
  TargetPopulationNode,
} from '../../__generated__/graphql';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: column;
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;
`;
const OverviewContainer = styled.div`
  display: flex;
  align-items: center;
  flex-direction: row;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface ProgramDetailsProps {
  targetPopulation: TargetPopulationNode;
}

export function TargetPopulationDetails({
  targetPopulation,
}: ProgramDetailsProps): React.ReactElement {
  const { createdBy, finalizedBy, approvedAt, finalizedAt, program } = targetPopulation;
  const closeDate = approvedAt ? moment(approvedAt).format('DD MMM YYYY') : '-';
  const sendBy = finalizedBy ? `${finalizedBy.firstName} ${finalizedBy.lastName}` : '-';
  const sendDate = finalizedAt ? moment(finalizedAt).format('DD MMM YYYY') : '-';
  const programName = program && program.name ? program.name : '-';
  return (
    <Container>
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
            <LabelizedField
              label='Programme'
              value={programName}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='Send by'
              value={sendBy}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='Send date'
              value={sendDate}
            />
          </Grid>
        </Grid>
      </OverviewContainer>
    </Container>
  );
}
