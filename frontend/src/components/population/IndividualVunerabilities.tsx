import React from 'react';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import { Typography } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';
import {
  IndividualNode,
  useAllIndividualsFlexFieldsAttributesQuery,
} from '../../__generated__/graphql';
import { getFlexFieldTextValue } from '../../utils/utils';

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
  const { data, loading } = useAllIndividualsFlexFieldsAttributesQuery();
  if (loading) {
    return null;
  }
  const fieldsDict = data.allIndividualsFlexFieldsAttributes.reduce(
    (previousValue, currentValue) => {
      // eslint-disable-next-line no-param-reassign
      previousValue[currentValue.name] = currentValue;
      return previousValue;
    },
    {},
  );

  const fields = Object.entries(individual.flexFields || {}).map(
    // eslint-disable-next-line array-callback-return,consistent-return
    ([key, value]: [string, string | string[]]) => {
      const flexFieldAttribute = fieldsDict[key];
      if (typeof flexFieldAttribute !== 'undefined') {
        return (
          <LabelizedField
            key={key}
            label={key.replaceAll('_i_f', '').replace(/_/g, ' ')}
            value={getFlexFieldTextValue(key, value, flexFieldAttribute)}
          />
        );
      }
    },
  );
  return (
    <div>
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
    </div>
  );
}
