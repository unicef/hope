import { Grid2 as Grid } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { LabelizedField } from '@core/LabelizedField';
import { DashboardCard, CardTitle, CardAmountSmaller } from './DashboardCard';
import { ReactElement } from 'react';

interface GrievanceDashboardCardProps {
  topLabel: string;
  topNumber: number | string;
  systemGenerated: number | string;
  userGenerated: number | string;
  dataCy?: string;
}

export function GrievanceDashboardCard({
  topLabel,
  topNumber,
  systemGenerated,
  userGenerated,
  dataCy,
}: GrievanceDashboardCardProps): ReactElement {
  const { t } = useTranslation();
  return (
    <DashboardCard color="#FFF">
      <CardTitle>{topLabel}</CardTitle>
      <Grid container alignItems="center">
        <Grid>
          <CardAmountSmaller data-cy={`${dataCy}-top-number`}>
            {topNumber}
          </CardAmountSmaller>
        </Grid>
      </Grid>
      <Grid container alignItems="center">
        <Grid size={{ xs: 6 }} >
          <LabelizedField
            dataCy={`${dataCy}-system-generated`}
            label={t('SYSTEM-GENERATED')}
          >
            {systemGenerated}
          </LabelizedField>
        </Grid>
        <Grid size={{ xs: 6 }} >
          <LabelizedField
            dataCy={`${dataCy}-user-generated`}
            label={t('USER-GENERATED')}
          >
            {userGenerated}
          </LabelizedField>
        </Grid>
      </Grid>
    </DashboardCard>
  );
}
