import React from 'react';
import {Grid, Typography} from '@material-ui/core';
import styled from 'styled-components';
import Paper from '@material-ui/core/Paper';
import {LabelizedField} from '../../../../components/LabelizedField';
import {useRegistrationDataImportQuery} from '../../../../__generated__/graphql';
import {UniversalMoment} from '../../../../components/UniversalMoment';

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
  registrationDate: string;
  deviceid: string;
  start: string;
}

export function RegistrationDetails({
  hctId,
  registrationDate,
  deviceid,
  start,
}: RegistrationDetailsProps): React.ReactElement {
  const { data } = useRegistrationDataImportQuery({
    variables: {
      id: btoa(`RegistrationDataImportNode:${hctId}`),
    },
  });
  if (!data) {
    return null;
  }
  const { registrationDataImport } = data;
  return (
    <Overview>
      <Title>
        <Typography variant='h6'>Registration Details</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid item xs={4}>
          <LabelizedField label='Source'>
            {registrationDataImport.dataSource}
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Title'>
            {registrationDataImport.name}
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label='Registered Date'>
            <UniversalMoment>{registrationDate}</UniversalMoment>
          </LabelizedField>
        </Grid>
      </Grid>
      {registrationDataImport.dataSource === 'XLS' ? null : (
        <>
          <hr />
          <Typography variant='h6'>Data Collection</Typography>
          <Grid container spacing={6}>
            <Grid item xs={4}>
              <LabelizedField label='Start time'>
                <UniversalMoment>{start}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label='End time'>
                <UniversalMoment>{registrationDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label='Device ID'>
                {deviceid}
              </LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label='User name'>
                {`${registrationDataImport.importedBy.firstName} ${registrationDataImport.importedBy.lastName}`}
              </LabelizedField>
            </Grid>
          </Grid>
        </>
      )}
    </Overview>
  );
}
