import { Grid, Typography } from '@material-ui/core';
import Paper from '@material-ui/core/Paper';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LabelizedField } from '../../../core/LabelizedField';
import { UniversalMoment } from '../../../core/UniversalMoment';
import { useRegistrationDataImportQuery } from '../../../../__generated__/graphql';
import { Title } from '../../../core/Title';

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
  rowId: number;
  koboAssetId: string;
}

export function RegistrationDetails({
  hctId,
  registrationDate,
  deviceid,
  start,
  rowId,
  koboAssetId,
}: RegistrationDetailsProps): React.ReactElement {
  const { t } = useTranslation();
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
        <Typography variant='h6'>{t('Registration Details')}</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid item xs={4}>
          <LabelizedField label={t('Source')}>
            {registrationDataImport.dataSource}
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label={t('Title')}>
            {registrationDataImport.name}
          </LabelizedField>
        </Grid>
        <Grid item xs={4}>
          <LabelizedField label={t('Registered Date')}>
            <UniversalMoment>{registrationDate}</UniversalMoment>
          </LabelizedField>
        </Grid>
      </Grid>
      {registrationDataImport.dataSource === 'XLS' ? null : (
        <>
          <hr />
          <Typography variant='h6'>{t('Data Collection')}</Typography>
          <Grid container spacing={6}>
            <Grid item xs={4}>
              <LabelizedField label={t('Start time')}>
                <UniversalMoment>{start}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label={t('End time')}>
                <UniversalMoment>{registrationDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label={t('Device ID')}>{deviceid}</LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label={t('Row ID')}>{rowId}</LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label={t('Kobo Asset ID')}>
                {koboAssetId}
              </LabelizedField>
            </Grid>
            <Grid item xs={4}>
              <LabelizedField label={t('User name')}>
                {`${registrationDataImport.importedBy?.firstName} ${registrationDataImport.importedBy?.lastName}`}
              </LabelizedField>
            </Grid>
          </Grid>
        </>
      )}
    </Overview>
  );
}
