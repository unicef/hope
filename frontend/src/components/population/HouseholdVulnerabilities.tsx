import React from 'react';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import { Typography } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';
import { Missing } from '../Missing';
import { HouseholdDetailedFragment } from '../../__generated__/graphql';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-top: 20px;
  &:first-child {
    margin-top: 0px;
  }
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface HouseholdVulnerabilities {
  household: HouseholdDetailedFragment;
}

export function HouseholdVulnerabilities({ household }): React.ReactElement {
  const fields = [];
  // eslint-disable-next-line guard-for-in,no-restricted-syntax
  for (const flexFieldKey in household.flexFields) {
    fields.push(
      <LabelizedField
        label={flexFieldKey}
        value={household.flexFields[flexFieldKey] || '-'}
      />,
    );
  }
  return (
    <div>
      <Overview>
        <Title>
          <Typography variant='h6'>Vulnerabilities</Typography>
        </Title>
        <Grid container spacing={6}>
          <Grid item xs={4}>
            {fields}
          </Grid>
        </Grid>
      </Overview>
    </div>
  );
}
