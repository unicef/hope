import React from 'react';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import { Typography } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';
import { IndividualNode } from '../../__generated__/graphql';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-top: ${({ theme }) => theme.spacing(6)}px;
  margin-bottom: ${({ theme }) => theme.spacing(6)}px;
`;

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

interface IndividualVulnerabilitesProps {
  individual: IndividualNode;
}

export function IndividualVulnerabilities({
  individual,
}: IndividualVulnerabilitesProps): React.ReactElement {
  const fields = [];
  // eslint-disable-next-line guard-for-in,no-restricted-syntax
  for (const flexFieldKey in individual.flexFields) {
    fields.push(
      <LabelizedField
        label={flexFieldKey}
        value={individual.flexFields[flexFieldKey] || '-'}
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
