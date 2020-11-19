import { Grid, Paper, Typography } from '@material-ui/core';
import styled from 'styled-components';
import React from 'react';
import {
  GrievanceTicketQuery,
  useAllAddIndividualFieldsQuery,
} from '../../__generated__/graphql';
import { LabelizedField } from '../LabelizedField';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function AddIndividualGrievanceDetails({
  ticket,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}): React.ReactElement {
  const { data, loading } = useAllAddIndividualFieldsQuery();
  if (loading) {
    return null;
  }
  const fieldsDict = data.allAddIndividualsFieldsAttributes.reduce(
    (previousValue, currentValue) => {
      // eslint-disable-next-line no-param-reassign
      previousValue[currentValue.name] = currentValue;
      return previousValue;
    },
    {},
  );
  const labels = Object.entries(
    ticket.addIndividualTicketDetails?.individualData || {},
  ).map(([key, value]) => {
    let textValue = value;
    const fieldAttribute = fieldsDict[key];
    if (fieldAttribute.type === 'SELECT_ONE') {
      textValue = fieldAttribute.choices.find((item) => item.value === value)
        .labelEn;
    }
    return (
      <Grid key={key} item xs={6}>
        <LabelizedField label={key.replace(/_/g, ' ')} value={textValue} />
      </Grid>
    );
  });
  return (
    <StyledBox>
      <Title>
        <Typography variant='h6'>Individual Data</Typography>
      </Title>
      <Grid container spacing={6}>
        {labels}
      </Grid>
    </StyledBox>
  );
}
