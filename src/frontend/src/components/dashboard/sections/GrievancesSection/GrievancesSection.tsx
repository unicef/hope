import { Grid2 as Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { formatNumber } from '@utils/utils';
import { AllChartsQuery } from '@generated/graphql';
import { GrievancesChart } from '../../charts/GrievancesChart';
import { DashboardPaper } from '../../DashboardPaper';
import { ReactElement } from 'react';

const CardTitleSmaller = styled.div`
  text-transform: capitalize;
  color: #6f6f6f;
  font-weight: 500;
  font-size: 11px;
`;

interface GrievancesSectionProps {
  data: AllChartsQuery['chartGrievances'];
}

export function GrievancesSection({
  data,
}: GrievancesSectionProps): ReactElement {
  const { t } = useTranslation();
  if (!data) return null;
  return (
    <DashboardPaper title="Grievances and Feedback">
      <Grid container spacing={3}>
        <Grid size={{ xs:6 }}>
          <CardTitleSmaller>{t('TOTAL NUMBER OF GRIEVANCES')}</CardTitleSmaller>
          <Typography variant="caption" data-cy="total-number-of-grievances">
            {formatNumber(data?.totalNumberOfGrievances)}
          </Typography>
        </Grid>
        <Grid size={{ xs:6 }}>
          <CardTitleSmaller>{t('TOTAL NUMBER OF FEEDBACK')}</CardTitleSmaller>
          <Typography variant="caption" data-cy="total-number-of-feedback">
            {formatNumber(data?.totalNumberOfFeedback)}
          </Typography>
        </Grid>
      </Grid>
      <GrievancesChart data={data} />
      <CardTitleSmaller>
        {t('NUMBER OF OPEN SENSITIVE GRIEVANCES')}
      </CardTitleSmaller>
      <Typography variant="caption">
        {formatNumber(data?.totalNumberOfOpenSensitive)}
      </Typography>
    </DashboardPaper>
  );
}
