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
  return (
    <Container>
      <Title>
        <Typography variant='h6'>Details</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
        <Grid item xs={4}>
            <LabelizedField
              label='Target population used in'
              value='some random id'
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='Vulnerability score'
              value='some random score'
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='Programme'
              value='some random programme name'
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='Finalized by'
              value='name surname'
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='END DATE'
              value={moment(targetPopulation.createdAt).format('DD MMM YYYY')}
            />
          </Grid>
        </Grid>
      </OverviewContainer>
    </Container>
  );
}
