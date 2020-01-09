import React from 'react';
import styled from 'styled-components';
import { Grid, Typography } from '@material-ui/core';
import { StatusBox } from '../StatusBox';
import { programStatusToColor } from '../../utils/utils';
import { LabelizedField } from '../LabelizedField';

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

export function ProgramDetails(): React.ReactElement {
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
                  status='ACTIVE'
                  statusToColor={programStatusToColor}
                />
              </StatusContainer>
            </LabelizedField>
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='START DATE' value='01 Jan 2019' />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='END DATE' value='31 Jan 2019' />
          </Grid>

          <Grid item xs={4}>
            <LabelizedField label='Sector' value='Child Protection' />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Scope' value='Full' />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='Frequency of Payment' value='Regular' />
          </Grid>

          <Grid item xs={4}>
            <LabelizedField
              label='Administrative Areas of implementation'
              value='Lorem ipsum'
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField
              label='Description'
              value='Description of how to help young children in remote locations'
            />
          </Grid>
          <Grid item xs={4}>
            <LabelizedField label='CASH+' value='No' />
          </Grid>
        </Grid>
        <NumberOfHouseHolds>
          <LabelizedField label='Total Number of Households' value='-' />
        </NumberOfHouseHolds>
      </OverviewContainer>
    </Container>
  );
}
