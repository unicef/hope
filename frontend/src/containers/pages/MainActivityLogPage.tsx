import React, {useState} from 'react';
import { PageHeader } from '../../components/PageHeader';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { MainActivityLogTable } from '../tables/MainActivityLogTable/MainActivityLogTable';
import {LogEntryObject, useAllLogEntriesQuery} from "../../__generated__/graphql";
import {ActivityLogTable} from "../../components/ActivityLogTable/ActivityLogTable";

export const ActivityLogPage = () => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const { data, refetch } = useAllLogEntriesQuery({
    variables: {
      first: rowsPerPage,
    },
    fetchPolicy: 'network-only',
  });
  if (!data) {
    return null;
  }
  const { edges } = data.allLogEntries;
  const logEntries = edges.map((edge) => edge.node as LogEntryObject);
  return (
    <MainActivityLogTable
      totalCount={data.allLogEntries.totalCount}
      rowsPerPage={rowsPerPage}
      logEntries={logEntries}
      page={page}
      onChangePage={(event, newPage) => {
        const variables = {
          first: undefined,
          last: undefined,
          after: undefined,
          before: undefined,
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
          first: rowsPerPage,
          after: undefined,
          last: undefined,
          before: undefined,
        };
        refetch(variables);
      }}
    />
  );
};
