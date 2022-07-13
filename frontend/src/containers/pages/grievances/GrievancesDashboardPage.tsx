import { Box, Grid } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { GrievanceDashboardCard } from '../../../components/grievances/GrievancesDashboard/GrievanceDashboardCard';
import { TicketsByCategorySection } from '../../../components/grievances/GrievancesDashboard/sections/TicketsByCategorySection/TicketsByCategorySection';
import { TicketsByLocationAndCategorySection } from '../../../components/grievances/GrievancesDashboard/sections/TicketsByLocationAndCategorySection/TicketsByLocationAndCategorySection';
import { TicketsByStatusSection } from '../../../components/grievances/GrievancesDashboard/sections/TicketsByStatusSection/TicketsByStatusSection';
import { hasPermissionInModule } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useAllGrievanceDashboardChartsQuery } from '../../../__generated__/graphql';

export const GrievancesDashboardPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { data, loading } = useAllGrievanceDashboardChartsQuery({
    variables: { businessAreaSlug: businessArea },
    fetchPolicy: 'network-only',
  });

  if (!data || permissions === null) return null;
  if (loading) return <LoadingComponent />;
  if (!hasPermissionInModule('GRIEVANCES_VIEW_LIST', permissions))
    return <PermissionDenied />;
  const {
    ticketsByCategory,
    ticketsByLocationAndCategory,
    ticketsByStatus,
    ticketsByType,
  } = data;

  return (
    <>
      <PageHeader title={t('Grievance Dashboard')} />
      <Grid container spacing={3}>
        <Grid item xs={4}>
          <Box p={3}>
            <GrievanceDashboardCard
              topLabel={t('TOTAL NUMBER OF TICKETS')}
              topNumber={
                ticketsByType.systemGeneratedCount +
                ticketsByType.userGeneratedCount
              }
              systemGenerated={ticketsByType.systemGeneratedCount}
              userGenerated={ticketsByType.userGeneratedCount}
            />
          </Box>
          <Box p={3}>
            <GrievanceDashboardCard
              topLabel={t('TOTAL NUMBER OF CLOSED TICKETS')}
              topNumber={
                ticketsByType.closedSystemGeneratedCount +
                ticketsByType.closedUserGeneratedCount
              }
              systemGenerated={ticketsByType.closedSystemGeneratedCount}
              userGenerated={ticketsByType.closedUserGeneratedCount}
            />
          </Box>
          <Box p={3}>
            <GrievanceDashboardCard
              topLabel={t('TICKETS AVERAGE RESOLUTION')}
              topNumber={`${ticketsByType.systemGeneratedAvgResolution +
                ticketsByType.userGeneratedAvgResolution} days`}
              systemGenerated={`${ticketsByType.systemGeneratedAvgResolution} days`}
              userGenerated={`${ticketsByType.userGeneratedAvgResolution} days`}
            />
          </Box>
          <Box p={3}>
            <TicketsByStatusSection data={ticketsByStatus} />
          </Box>
        </Grid>
        <Grid item xs={8}>
          <Box p={3}>
            <TicketsByCategorySection data={ticketsByCategory} />
          </Box>
          <Box p={3}>
            <TicketsByLocationAndCategorySection
              data={ticketsByLocationAndCategory}
            />
          </Box>
        </Grid>
      </Grid>
    </>
  );
};
