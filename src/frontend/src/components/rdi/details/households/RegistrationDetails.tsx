import { Grid2 as Grid, Theme, Typography } from '@mui/material';
import Paper from '@mui/material/Paper';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LabelizedField } from '@core/LabelizedField';
import { UniversalMoment } from '@core/UniversalMoment';
import { Title } from '@core/Title';
import { ReactElement } from 'react';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

const Overview = styled(Paper)<{ theme?: Theme }>`
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
  const { businessArea, programId } = useBaseUrl();

  const { data, isLoading } = useQuery({
    queryKey: ['registrationDataImport', businessArea, programId, hctId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsRegistrationDataImportsRetrieve({
        businessAreaSlug: businessArea,
        id: hctId,
        programSlug: programId,
      }),
    enabled: !!businessArea && !!programId && !!hctId,
  });

  if (isLoading || !data) {
    return null;
  }

  return (
    <Overview>
      <Title>
        <Typography variant="h6">{t('Registration Details')}</Typography>
      </Title>
      <Grid container spacing={6}>
        <Grid size={{ xs: 4 }}>
          <LabelizedField label={t('Source')}>{data.dataSource}</LabelizedField>
        </Grid>
        <Grid size={{ xs: 4 }}>
          <LabelizedField label={t('Title')}>{data.name}</LabelizedField>
        </Grid>
        <Grid size={{ xs: 4 }}>
          <LabelizedField label={t('Registered Date')}>
            <UniversalMoment>{registrationDate}</UniversalMoment>
          </LabelizedField>
        </Grid>
      </Grid>
      {data.dataSource === 'XLS' ? null : (
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
                {data.importedBy || ''}
              </LabelizedField>
            </Grid>
          </Grid>
        </>
      )}
    </Overview>
  );
}
