import { Grid } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { LabelizedField } from '@core/LabelizedField';
import { DashboardCard, CardTitle, CardAmountSmaller } from './DashboardCard';

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
}: GrievanceDashboardCardProps): React.ReactElement {
  const { t } = useTranslation();
  return (
    <DashboardCard color="#FFF">
      <CardTitle>{topLabel}</CardTitle>
      <Grid container alignItems="center">
        <Grid item>
          <CardAmountSmaller data-cy={`${dataCy}-top-number`}>
            {topNumber}
          </CardAmountSmaller>
        </Grid>
      </Grid>
      <Grid container alignItems="center">
        <Grid xs={6} item>
          <LabelizedField
            dataCy={`${dataCy}-system-generated`}
            label={t('SYSTEM-GENERATED')}
          >
            {systemGenerated}
          </LabelizedField>
        </Grid>
        <Grid xs={6} item>
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
