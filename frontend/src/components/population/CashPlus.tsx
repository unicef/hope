import React from 'react';
import styled from 'styled-components';
import { Typography, Paper, Grid } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-bottom: ${({ theme }) => theme.spacing(6)}px;
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function CashPlus({ individual }): React.ReactElement {
  const { enrolledInNutritionProgramme, administrationOfRutf } = individual;
  return (
    <Overview>
      <Title>
        <Typography variant='h6'>Cash+</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid item xs={4}>
          <LabelizedField
            label='Enrolled in nutrition programme'
            value={enrolledInNutritionProgramme ? 'YES' : 'NO'}
          />
        </Grid>
        <Grid item xs={4}>
          <LabelizedField
            label='Administratiion of rutf'
            value={administrationOfRutf ? 'YES' : 'NO'}
          />
        </Grid>
      </Grid>
    </Overview>
  );
}
