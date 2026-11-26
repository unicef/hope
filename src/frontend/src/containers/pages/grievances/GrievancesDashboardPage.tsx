import Box from '@mui/material/Box';
import { useTranslation } from 'react-i18next';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TableWrapper } from '@components/core/TableWrapper';
import { GrievanceDashboardCard } from '@components/grievances/GrievancesDashboard/GrievanceDashboardCard';
import { TicketsByCategorySection } from '@components/grievances/GrievancesDashboard/sections/TicketsByCategorySection/TicketsByCategorySection';
import { TicketsByLocationAndCategorySection } from '@components/grievances/GrievancesDashboard/sections/TicketsByLocationAndCategorySection/TicketsByLocationAndCategorySection';
import { TicketsByStatusSection } from '@components/grievances/GrievancesDashboard/sections/TicketsByStatusSection/TicketsByStatusSection';
import { usePermissions } from '@hooks/usePermissions';
import {
  GRIEVANCES_VIEW_DETAILS_PERMISSIONS,
  GRIEVANCES_VIEW_LIST_PERMISSIONS,
  hasPermissions,
} from '../../../config/permissions';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { useBaseUrl } from '@hooks/useBaseUrl';
import type { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { formatFigure } from '@utils/utils';
import {
  ResponsiveGrid,
  ResponsiveGridContainer,
  responsiveValue,
} from 'src/responsive';

function GrievancesDashboardPage(): ReactElement {
  const { t } = useTranslation();
  const { businessAreaSlug, programCode, isAllPrograms } = useBaseUrl();
  const permissions = usePermissions();

  // Use program-specific dashboard if we're in a specific program context,
  // otherwise use global dashboard
  const { data, isLoading: loading } = useQuery({
    queryKey: isAllPrograms
      ? restQueryKey(
          RestService.restBusinessAreasGrievanceTicketsDashboardRetrieve,
          { businessAreaSlug },
        )
      : restQueryKey(
          RestService.restBusinessAreasProgramsGrievanceTicketsDashboardRetrieve,
          { businessAreaSlug, programCode },
        ),
    queryFn: () => {
      if (isAllPrograms) {
        return RestService.restBusinessAreasGrievanceTicketsDashboardRetrieve({
          businessAreaSlug,
        });
      } else {
        return RestService.restBusinessAreasProgramsGrievanceTicketsDashboardRetrieve(
          {
            businessAreaSlug,
            programCode,
          },
        );
      }
    },
    refetchOnMount: 'always',
  });

  if (!data || permissions === null) return null;
  if (loading) return <LoadingComponent />;
  const grievancesViewPermissions = [
    ...GRIEVANCES_VIEW_LIST_PERMISSIONS,
    ...GRIEVANCES_VIEW_DETAILS_PERMISSIONS,
  ];
  const hasGrievancesViewPermission = hasPermissions(
    grievancesViewPermissions,
    permissions,
  );

  if (!hasGrievancesViewPermission)
    return <PermissionDenied permission={grievancesViewPermissions} />;

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
        <ResponsiveGridContainer spacing={2} sx={{ alignItems: 'stretch' }}>
          <ResponsiveGrid size="third">
            <Box
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <GrievanceDashboardCard
                topLabel={t('TOTAL NUMBER OF TICKETS')}
                topNumber={formatFigure(
                  systemGeneratedCount + userGeneratedCount,
                )}
                systemGenerated={formatFigure(systemGeneratedCount)}
                userGenerated={formatFigure(userGeneratedCount)}
                dataCy="total-number-of-tickets"
              />
              <GrievanceDashboardCard
                topLabel={t('TOTAL NUMBER OF CLOSED TICKETS')}
                topNumber={formatFigure(numberOfClosedTickets)}
                systemGenerated={formatFigure(closedSystemGeneratedCount)}
                userGenerated={formatFigure(closedUserGeneratedCount)}
                dataCy="total-number-of-closed-tickets"
              />
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
          </ResponsiveGrid>
          <ResponsiveGrid size="twoThirds">
            <Box sx={{ ml: responsiveValue(0, 3) }}>
              <TicketsByCategorySection data={ticketsByCategory} />
            </Box>
          </ResponsiveGrid>
        </ResponsiveGridContainer>
        <ResponsiveGridContainer spacing={2} sx={{ mt: 5 }}>
          <ResponsiveGrid size="third">
            <TicketsByStatusSection data={ticketsByStatus} />
          </ResponsiveGrid>
          <ResponsiveGrid size="twoThirds">
            <Box sx={{ ml: responsiveValue(0, 3) }}>
              <TicketsByLocationAndCategorySection
                data={ticketsByLocationAndCategory}
              />
            </Box>
          </ResponsiveGrid>
        </ResponsiveGridContainer>
      </TableWrapper>
    </>
  );
}

export default withErrorBoundary(
  GrievancesDashboardPage,
  'GrievancesDashboardPage',
);
