import React from 'react';
import styled from 'styled-components';
import { Grid, Typography } from '@material-ui/core';
import { StatusBox } from '../StatusBox';
import { programStatusToColor } from '../../utils/utils';
import { LabelizedField } from '../LabelizedField';
import { ProgramNode } from '../../__generated__/graphql';
import moment from 'moment';

const Container = styled.div`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: 20px;
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

const StatusContainer = styled.div`
  width: 120px;
`;

const NumberOfHouseHolds = styled.div`
  padding: 25px;
  border-color: #b1b1b5;
  border-left-width: 1px;
  border-left-style: solid;
`;
const Title = styled.div`
  margin: 7px 0px 25px 0px;
`;

interface ProgramDetailsProps {
  program: ProgramNode;
}

export function ProgramDetails({
  program,
}: ProgramDetailsProps): React.ReactElement {
  return (
    <Container>
      <Title>
        <Typography variant='h6'>Programme Details</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={3}>
          <Grid item xs={4}>
            <LabelizedField label='status'>
              <StatusContainer>
                <StatusBox
                  status={program.status}
                  statusToColor={programStatusToColor}
                />
              </StatusContainer>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='START DATE' value={moment(program.startDate).format('MM/DD/YYYY')} />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='END DATE' value={moment(program.endDate).format('MM/DD/YYYY')} />
          </Grid>

          <Grid item xs={4}>
            <LabelizedField label='Sector' value={program.sector} />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Scope' value={program.scope} />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='Frequency of Payment'
              value={program.frequencyOfPayments}
            />
          </Grid>

          <Grid item xs={4}>
            <LabelizedField
              label='Administrative Areas of implementation'
              value={program.location.name}
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Description' value={program.description} />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='CASH+'
              value={program.cashPlus ? 'Yes' : 'No'}
            />
          </Grid>
        </Grid>
        <NumberOfHouseHolds>
          <LabelizedField
            label='Total Number of Households'
            value={program.totalNumberOfHouseholds}
          />
        </NumberOfHouseHolds>
      </OverviewContainer>
    </Container>
  );
}
