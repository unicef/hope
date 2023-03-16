import { Paper } from '@material-ui/core';
import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ActivityLogPageFilters } from '../../../components/core/ActivityLogPageFilters';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { EmptyTable } from '../../../components/core/Table/EmptyTable';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../utils/utils';
import {
  LogEntryNode,
  useAllLogEntriesQuery,
} from '../../../__generated__/graphql';
import { MainActivityLogTable } from '../../tables/MainActivityLogTable/MainActivityLogTable';

export const StyledPaper = styled(Paper)`
  margin: 20px;
`;
// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function filtersToVariables(filters) {
  const variables: { module?: string; search?: string } = {};
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

const initialFilter = { search: '', module: '' };

export const ActivityLogPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const debouncedFilter = useDebounce(filter, 700);

  const { data, refetch, loading } = useAllLogEntriesQuery({
    variables: {
      businessArea,
      first: rowsPerPage,
      last: undefined,
      after: undefined,
      before: undefined,
      ...filtersToVariables(debouncedFilter),
    },
    notifyOnNetworkStatusChange: true,
    fetchPolicy: 'network-only',
  });

  useEffect(() => {
    // we need to check for permission before refetch, otherwise returned permission denied error
    // breaks the page
    if (
      permissions &&
      hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions)
    ) {
      setPage(0);
      refetch({
        businessArea,
        first: rowsPerPage,
        last: undefined,
        after: undefined,
        before: undefined,
        ...filtersToVariables(debouncedFilter),
      });
    }
  }, [debouncedFilter, businessArea, refetch, permissions, rowsPerPage]);

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions))
    return <PermissionDenied />;

  if (!data && !loading) {
    return <EmptyTable />;
  }
  if (!data && loading) return <LoadingComponent />;
  const { edges } = data.allLogEntries;
  const { logEntryActionChoices } = data;
  const logEntries = edges.map((edge) => edge.node as LogEntryNode);
  return (
    <>
      <PageHeader title={t('Activity Log')} />
      <ActivityLogPageFilters filter={filter} onFilterChange={setFilter} />
      <StyledPaper>
        <MainActivityLogTable
          totalCount={data.allLogEntries.totalCount}
          rowsPerPage={rowsPerPage}
          logEntries={logEntries}
          actionChoices={logEntryActionChoices}
          page={page}
          loading={loading}
          onChangePage={(event, newPage) => {
            const variables = {
              businessArea,
              first: undefined,
              last: undefined,
              after: undefined,
              before: undefined,
              ...filtersToVariables(debouncedFilter),
            };
            if (newPage < page) {
              variables.last = rowsPerPage;
              variables.before = edges[0].cursor;
            } else {
              variables.after = edges[edges.length - 1].cursor;
              variables.first = rowsPerPage;
            }
            setPage(newPage);
            refetch(variables);
          }}
          onChangeRowsPerPage={(event) => {
            const value = parseInt(event.target.value, 10);
            setRowsPerPage(value);
            setPage(0);
            const variables = {
              businessArea,
              first: rowsPerPage,
              after: undefined,
              last: undefined,
              before: undefined,
              ...filtersToVariables(debouncedFilter),
            };
            refetch(variables);
          }}
        />
      </StyledPaper>
    </>
  );
};
