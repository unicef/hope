import { Grid2 as Grid, Typography } from '@mui/material';
import Paper from '@mui/material/Paper';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LabelizedField } from '@core/LabelizedField';
import { UniversalMoment } from '@core/UniversalMoment';
import { useRegistrationDataImportQuery } from '@generated/graphql';
import { Title } from '@core/Title';
import { ReactElement } from 'react';

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
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
  detailId: string;
}

export function RegistrationDetails({
  hctId,
  registrationDate,
  deviceid,
  start,
  detailId,
}: RegistrationDetailsProps): ReactElement {
  const { t } = useTranslation();
  const { data } = useRegistrationDataImportQuery({
    variables: {
      id: hctId,
    },
  });
  if (!data) {
    return null;
  }
  const { registrationDataImport } = data;
  return (
    <Overview>
      <Title>
        <Typography variant="h6">{t('Registration Details')}</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid size={{ xs: 4 }}>
          <LabelizedField label={t('Source')}>
            {registrationDataImport.dataSource}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 4 }}>
          <LabelizedField label={t('Title')}>
            {registrationDataImport.name}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 4 }}>
          <LabelizedField label={t('Registered Date')}>
            <UniversalMoment>{registrationDate}</UniversalMoment>
          </LabelizedField>
        </Grid>
      </Grid>
      {registrationDataImport.dataSource === 'XLS' ? null : (
        <>
          <hr />
          <Typography variant="h6">{t('Data Collection')}</Typography>
          <Grid container spacing={6}>
            <Grid size={{ xs: 4 }}>
              <LabelizedField label={t('Start time')}>
                <UniversalMoment>{start}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 4 }}>
              <LabelizedField label={t('End time')}>
                <UniversalMoment>{registrationDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 4 }}>
              <LabelizedField label={t('Device ID')}>{deviceid}</LabelizedField>
            </Grid>
            <Grid size={{ xs: 4 }}>
              <LabelizedField label={t('Detail ID')}>{detailId}</LabelizedField>
            </Grid>
            <Grid size={{ xs: 4 }}>
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
