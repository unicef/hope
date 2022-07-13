import { Box, Grid } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { GrievanceDashboardCard } from '../../../components/grievances/GrievancesDashboard/GrievanceDashboardCard';
import { TicketsByCategorySection } from '../../../components/grievances/GrievancesDashboard/sections/TicketsByCategorySection/TicketsByCategorySection';
import { TicketsByCategoryAndLocationSection } from '../../../components/grievances/GrievancesDashboard/sections/TicketsByCateogryAndLocationSection/TicketsByCategoryAndLocationSection';
import { TicketsByStatusSection } from '../../../components/grievances/GrievancesDashboard/sections/TicketsByStatusSection/TicketsByStatusSection';
import { hasPermissionInModule } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';

export const GrievancesDashboardPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  if (permissions === null) return null;
  if (!hasPermissionInModule('GRIEVANCES_VIEW_LIST', permissions))
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('Grievance Dashboard')} />
      <Grid container spacing={3}>
        <Grid item xs={4}>
          <Box p={3}>
            <GrievanceDashboardCard
              topLabel={t('TOTAL NUMBER OF TICKETS')}
              topNumber={0}
              systemGenerated={0}
              userGenerated={0}
            />
          </Box>
          <Box p={3}>
            <GrievanceDashboardCard
              topLabel={t('TOTAL NUMBER OF CLOSED TICKETS')}
              topNumber={0}
              systemGenerated={0}
              userGenerated={0}
            />
          </Box>
          <Box p={3}>
            <GrievanceDashboardCard
              topLabel={t('TICKETS AVERAGE RESOLUTION')}
              topNumber={0}
              systemGenerated={0}
              userGenerated={0}
            />
          </Box>
          <Box p={3}>
            <TicketsByStatusSection data={null} />
          </Box>
        </Grid>
        <Grid item xs={8}>
          <Box p={3}>
            <TicketsByCategorySection data={null} />
          </Box>
          <Box p={3}>
            <TicketsByCategoryAndLocationSection data={null} />
          </Box>
        </Grid>
      </Grid>
    </>
  );
};
