import { Paper } from '@mui/material';
import { ReactElement, useState, ChangeEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { ActivityLogPageFilters } from '@components/core/ActivityLogPageFilters';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { EmptyTable } from '@components/core/Table/EmptyTable';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { MainActivityLogTable } from '../../tables/MainActivityLogTable/MainActivityLogTable';
import { useBaseUrl } from '@hooks/useBaseUrl';

export const StyledPaper = styled(Paper)`
  margin: 20px;
`;
// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function filtersToVariables(filters) {
  const variables: { module?: string; search?: string; userId?: string } = {};
  if (filters.userId !== '') {
    variables.userId = filters.userId;
  } else {
    variables.userId = undefined;
  }

  if (filters.module !== '') {
    variables.module = filters.module;
  } else {
    variables.module = undefined;
  }

  if (
    filters.search !== '' &&
    filters.search !== null &&
    filters.search !== undefined
  ) {
    variables.search = filters.search;
  } else {
    variables.search = undefined;
  }
  return variables;
}

export function ActivityLogPage(): ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const { businessArea, programId, isAllPrograms } = useBaseUrl();
  const initialFilter = { search: '', module: '', userId: '' };
  const permissions = usePermissions();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  // Query for activity logs based on whether it's all programs or a specific program
  const { data: logsData, isLoading: logsLoading } = useQuery({
    queryKey: [
      'activityLogs',
      businessArea,
      programId,
      isAllPrograms,
      page,
      rowsPerPage,
      appliedFilter,
    ],
    queryFn: () => {
      const variables = {
        businessAreaSlug: businessArea,
        limit: rowsPerPage,
        offset: page * rowsPerPage,
        ...filtersToVariables(appliedFilter),
      };

      if (isAllPrograms) {
        return RestService.restBusinessAreasActivityLogsList(variables);
      } else {
        return RestService.restBusinessAreasProgramsActivityLogsList({
          ...variables,
          programSlug: programId,
        });
      }
    },
    enabled: !!(
      businessArea &&
      permissions &&
      hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions)
    ),
  });

  const { data: countData } = useQuery({
    queryKey: ['activityLogsCount', businessArea, programId, isAllPrograms],
    queryFn: () => {
      if (isAllPrograms) {
        return RestService.restBusinessAreasActivityLogsCountRetrieve({
          businessAreaSlug: businessArea,
        });
      } else {
        return RestService.restBusinessAreasProgramsActivityLogsCountRetrieve({
          businessAreaSlug: businessArea,
          programSlug: programId,
        });
      }
    },
    enabled: !!(
      businessArea &&
      permissions &&
      hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions)
    ),
  });

  const { data: actionChoicesData } = useQuery({
    queryKey: [
      'activityLogsActionChoices',
      businessArea,
      programId,
      isAllPrograms,
    ],
    queryFn: () => {
      if (isAllPrograms) {
        return RestService.restBusinessAreasActivityLogsActionChoicesList({
          businessAreaSlug: businessArea,
        });
      } else {
        return RestService.restBusinessAreasProgramsActivityLogsActionChoicesList(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
          },
        );
      }
    },
    enabled: !!(
      businessArea &&
      permissions &&
      hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions)
    ),
  });

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions))
    return <PermissionDenied />;

  if (!logsData && !logsLoading) {
    return <EmptyTable />;
  }
  if (!logsData && logsLoading) return <LoadingComponent />;

  // Use REST API LogEntry data directly
  const logEntries = logsData.results;

  // Transform action choices from REST format to expected format
  const actionChoices = actionChoicesData?.results || [];

  // Get total count for pagination
  const totalCount = countData?.count ?? 0;

  const handlePageChange = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(event.target.value, 10);
    setRowsPerPage(value);
    setPage(0);
  };

  return (
    <>
      <PageHeader title={t('Activity Log')} />
      <ActivityLogPageFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <StyledPaper>
        <MainActivityLogTable
          totalCount={totalCount}
          rowsPerPage={rowsPerPage}
          logEntries={logEntries}
          actionChoices={actionChoices}
          page={page}
          loading={logsLoading}
          onChangePage={handlePageChange}
          onChangeRowsPerPage={handleRowsPerPageChange}
        />
      </StyledPaper>
    </>
  );
}
