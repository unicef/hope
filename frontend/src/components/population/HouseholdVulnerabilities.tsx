import React from 'react';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import { Typography } from '@material-ui/core';
import { LabelizedField } from '../LabelizedField';
import {
  HouseholdDetailedFragment,
  useAllHouseholdsFlexFieldsAttributesQuery,
} from '../../__generated__/graphql';
import { getFlexFieldTextValue } from '../../utils/utils';

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

interface HouseholdVulnerabilitiesProps {
  household: HouseholdDetailedFragment;
}

export function HouseholdVulnerabilities({
  household,
}: HouseholdVulnerabilitiesProps): React.ReactElement {
  const { data, loading } = useAllHouseholdsFlexFieldsAttributesQuery();
  if (loading) {
    return null;
  }
  const fieldsDict = data.allHouseholdsFlexFieldsAttributes.reduce(
    (previousValue, currentValue) => {
      // eslint-disable-next-line no-param-reassign
      previousValue[currentValue.name] = currentValue;
      return previousValue;
    },
    {},
  );
  const fields = Object.entries(household.flexFields || {}).map(
    ([key, value]: [string, string | string[]]) => {
      return (
        <LabelizedField
          key={key}
          label={key.replaceAll('_h_f', '').replace(/_/g, ' ')}
          value={getFlexFieldTextValue(key, value, fieldsDict[key])}
        />
      );
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
