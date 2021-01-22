import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { Paper } from '@material-ui/core';
import { MainActivityLogTable } from '../tables/MainActivityLogTable/MainActivityLogTable';
import {
  LogEntryNode,
  useAllLogEntriesQuery,
} from '../../__generated__/graphql';
import { PageHeader } from '../../components/PageHeader';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { ActivityLogPageFilters } from '../../components/ActivityLogPageFilters';
import { useDebounce } from '../../hooks/useDebounce';

export const StyledPaper = styled(Paper)`
  margin: 20px;
`;

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

export const ActivityLogPage = (): React.ReactElement => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const businessArea = useBusinessArea();
  const { data, refetch } = useAllLogEntriesQuery({
    variables: {
      businessArea,
      first: rowsPerPage,
    },
    fetchPolicy: 'network-only',
  });
  const [filters, setFilters] = useState({ search: null, module: '' });
  const debouncedFilters = useDebounce(filters, 700);
  useEffect(() => {
    console.log('xD', {
      businessArea,
      first: rowsPerPage,
      last: undefined,
      after: undefined,
      before: undefined,
      ...filtersToVariables(debouncedFilters),
    });
    refetch({
      businessArea,
      first: rowsPerPage,
      last: undefined,
      after: undefined,
      before: undefined,
      ...filtersToVariables(debouncedFilters),
    });
    // eslint-disable-next-line
  }, [debouncedFilters]);
  if (!data) {
    return null;
  }
  const { edges } = data.allLogEntries;
  const { logEntryActionChoices } = data;
  const logEntries = edges.map((edge) => edge.node as LogEntryNode);
  return (
    <>
      <PageHeader title='Activity Log' />
      <ActivityLogPageFilters filter={filters} onFilterChange={setFilters} />
      <StyledPaper>
        <MainActivityLogTable
          totalCount={data.allLogEntries.totalCount}
          rowsPerPage={rowsPerPage}
          logEntries={logEntries}
          actionChoices={logEntryActionChoices}
          page={page}
          onChangePage={(event, newPage) => {
            const variables = {
              businessArea,
              first: undefined,
              last: undefined,
              after: undefined,
              before: undefined,
              ...filtersToVariables(debouncedFilters),
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
              ...filtersToVariables(debouncedFilters),
            };
            refetch(variables);
          }}
        />
      </StyledPaper>
    </>
  );
};
