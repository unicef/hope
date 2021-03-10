import React from 'react';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import { Typography } from '@material-ui/core';
import { ImportedIndividualDetailedFragment } from '../../../../__generated__/graphql';
import { LabelizedField } from '../../../../components/LabelizedField';

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

interface RegistrationIndividualVulnerabilitiesProps {
  individual: ImportedIndividualDetailedFragment;
}

export function RegistrationIndividualVulnerabilities({
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  individual,
}: RegistrationIndividualVulnerabilitiesProps): React.ReactElement {
  const fields = Object.entries(individual.flexFields || {}).map(
    ([key, value]: [string, string | string[]]) => {
      return (
        <LabelizedField
          key={key}
          label={key.replaceAll('_i_f', '').replace(/_/g, ' ')}
          value={value}
        />
      );
    },
  );
  return (
    <Overview>
      <Title>
        <Typography variant='h6'>Vulnerabilities</Typography>
      </Title>
      <Grid container spacing={6}>
        {fields.map((field) => (
          <Grid item xs={4}>
            {field}
          </Grid>
        ))}
      </Grid>
    </Overview>
  );
}
