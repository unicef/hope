import { Box, Grid2 as Grid } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TableWrapper } from '@components/core/TableWrapper';
import { GrievanceDashboardCard } from '@components/grievances/GrievancesDashboard/GrievanceDashboardCard';
import { TicketsByCategorySection } from '@components/grievances/GrievancesDashboard/sections/TicketsByCategorySection/TicketsByCategorySection';
import { TicketsByLocationAndCategorySection } from '@components/grievances/GrievancesDashboard/sections/TicketsByLocationAndCategorySection/TicketsByLocationAndCategorySection';
import { TicketsByStatusSection } from '@components/grievances/GrievancesDashboard/sections/TicketsByStatusSection/TicketsByStatusSection';
import { hasPermissionInModule } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

function GrievancesDashboardPage(): ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const { data, isLoading: loading } = useQuery({
    queryKey: ['grievanceDashboard', businessArea],
    queryFn: () => RestService.restBusinessAreasGrievanceTicketsDashboardRetrieve({
      businessAreaSlug: businessArea,
    }),
    refetchOnMount: 'always',
  });

  if (!data || permissions === null) return null;
  if (loading) return <LoadingComponent />;
  if (!hasPermissionInModule('GRIEVANCES_VIEW_LIST', permissions))
    return <PermissionDenied />;

  const {
    ticketsByCategory,
    ticketsByLocationAndCategory,
    ticketsByStatus,
    ticketsByType: {
      userGeneratedCount,
      systemGeneratedCount,
      closedUserGeneratedCount,
      closedSystemGeneratedCount,
      userGeneratedAvgResolution,
      systemGeneratedAvgResolution,
    },
  } = data;

  // use weighted average to calculate average resolution time
  const userWeightedTime =
    userGeneratedAvgResolution * closedUserGeneratedCount;
  const systemWeightedTime =
    systemGeneratedAvgResolution * closedSystemGeneratedCount;
  const numberOfClosedTickets =
    closedUserGeneratedCount + closedSystemGeneratedCount;

  return (
    <>
      <PageHeader title={t('Grievance Dashboard')} />
      <TableWrapper>
        <Grid container spacing={2}>
          <Grid size={{ xs: 4 }}>
            <Box>
              <GrievanceDashboardCard
                topLabel={t('TOTAL NUMBER OF TICKETS')}
                topNumber={systemGeneratedCount + userGeneratedCount}
                systemGenerated={systemGeneratedCount}
                userGenerated={userGeneratedCount}
                dataCy="total-number-of-tickets"
              />
            </Box>
            <Box mt={5}>
              <GrievanceDashboardCard
                topLabel={t('TOTAL NUMBER OF CLOSED TICKETS')}
                topNumber={numberOfClosedTickets}
                systemGenerated={closedSystemGeneratedCount}
                userGenerated={closedUserGeneratedCount}
                dataCy="total-number-of-closed-tickets"
              />
            </Box>
            <Box mt={5}>
              <GrievanceDashboardCard
                topLabel={t('TICKETS AVERAGE RESOLUTION')}
                topNumber={`${
                  numberOfClosedTickets > 0
                    ? (
                        (userWeightedTime + systemWeightedTime) /
                        numberOfClosedTickets
                      ).toFixed(2)
                    : 0
                } days`}
                systemGenerated={`${systemGeneratedAvgResolution} days`}
                userGenerated={`${userGeneratedAvgResolution} days`}
                dataCy="tickets-average-resolution"
              />
            </Box>
            <Box mt={5}>
              <TicketsByStatusSection data={ticketsByStatus} />
            </Box>
          </Grid>
          <Grid size={{ xs:8 }}>
            <Box ml={3}>
              <TicketsByCategorySection data={ticketsByCategory} />
            </Box>
            <Box ml={3} mt={5}>
              <TicketsByLocationAndCategorySection
                data={ticketsByLocationAndCategory}
              />
            </Box>
          </Grid>
        </Grid>
      </TableWrapper>
    </>
  );
}

export default withErrorBoundary(
  GrievancesDashboardPage,
  'GrievancesDashboardPage',
);
