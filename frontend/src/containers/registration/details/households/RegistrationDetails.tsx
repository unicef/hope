import React from 'react';
import { ImportedIndividualsTable } from '../../tables/ImportedIndividualsTable';
import { Grid, Typography } from '@material-ui/core';
import { LabelizedField } from '../../../../components/LabelizedField';
import styled from 'styled-components';
import {
  RegistrationDetailedFragment,
  useRegistrationDataImportQuery,
} from '../../../../__generated__/graphql';
import Paper from "@material-ui/core/Paper";


const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  margin-top: 20px;
  &:first-child {
    margin-top: 0px;
  }
`;
interface RegistrationDetailsProps {
  hctId: string;
  registrationDate: string
}

export function RegistrationDetails({
  hctId,
                                        registrationDate
}: RegistrationDetailsProps): React.ReactElement {
  const { data } = useRegistrationDataImportQuery({
    variables: {
      id: btoa(`RegistrationDataImportNode:${hctId}`),
    },
  });
  if (!data) {
    return null;
  }
  const  {registrationDataImport} = data;
  return (
    <Overview>
      <Title>
        <Typography variant='h6'>Registration Details</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid item xs={4}>
          <LabelizedField label='Source'>
            <div>{registrationDataImport.dataSource}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Intake group name'>
            <div>{registrationDataImport.name}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Registered Date'>
            <div>{registrationDate}</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Number of Rooms'>
            <div>-</div>
          </LabelizedField>
        </Grid>
      </Grid>
      <hr />
      <Typography variant='h6'>Data Collection</Typography>
      <Grid container spacing={6}>
        <Grid item xs={4}>
          <LabelizedField label='Start time'>
            <div>-</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='End time'>
            <div>-</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Device ID'>
            <div>-</div>
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='User name'>
            <div>-</div>
          </LabelizedField>
        </Grid>
      </Grid>
    </Overview>
  );
}
