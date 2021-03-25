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
import { useArrayToDict } from '../../hooks/useArrayToDict';
import { LoadingComponent } from '../LoadingComponent';

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

const Image = styled.img`
  max-width: 150px;
`;

interface HouseholdVulnerabilitiesProps {
  household: HouseholdDetailedFragment;
}

export function HouseholdVulnerabilities({
  household,
}: HouseholdVulnerabilitiesProps): React.ReactElement {
  const { data, loading } = useAllHouseholdsFlexFieldsAttributesQuery();
  const flexAttributesDict = useArrayToDict(
    data?.allHouseholdsFlexFieldsAttributes,
    'name',
    '*',
  );

  if (loading) {
    return <LoadingComponent />;
  }

  if (!data || !flexAttributesDict) {
    return null;
  }
  const fields = Object.entries(household.flexFields || {}).map(
    ([key, value]: [string, string | string[]]) => {
      if (flexAttributesDict[key].type === 'IMAGE') {
        return (
          <LabelizedField
            key={key}
            label={key.replaceAll('_i_f', '').replace(/_/g, ' ')}
          >
            <Image src={value} />
          </LabelizedField>
        );
      }
      if (
        flexAttributesDict[key].type === 'SELECT_MANY' ||
        flexAttributesDict[key].type === 'SELECT_ONE'
      ) {
        let newValue =
          flexAttributesDict[key].choices.find((item) => item.value === value)
            ?.labelEn || '-';
        if (value instanceof Array) {
          newValue = value
            .map(
              (choice) =>
                flexAttributesDict[key].choices.find(
                  (item) => item.value === choice,
                )?.labelEn || '-',
            )
            .join(', ');
        }
        return (
          <LabelizedField
            key={key}
            label={key.replaceAll('_i_f', '').replace(/_/g, ' ')}
            value={newValue}
          />
        );
      }
      return (
        <LabelizedField
          key={key}
          label={key.replaceAll('_h_f', '').replace(/_/g, ' ')}
          value={value}
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
