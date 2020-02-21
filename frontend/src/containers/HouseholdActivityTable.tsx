import React, { ReactElement, useState } from 'react';
import {
  LogEntryObject,
  useAllLogEntriesQuery,
  HouseholdNode,
} from '../__generated__/graphql';
import { ActivityLogTable } from '../components/ActivityLogTable/ActivityLogTable';

interface HouseholdActivityTableProp {
  household: HouseholdNode;
}
export function HouseholdActivityTable({
  household,
}: HouseholdActivityTableProp): ReactElement {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const { data, fetchMore } = useAllLogEntriesQuery({
    variables: {
      objectId: household.id,
      count: rowsPerPage,
    },
    fetchPolicy: 'network-only',
  });
  if (!data) {
    return null;
  }
  const { edges } = data.allLogEntries;
  const logEntries = edges.map((edge) => edge.node as LogEntryObject);
  return (
    <ActivityLogTable
      totalCount={data.allLogEntries.totalCount}
      rowsPerPage={rowsPerPage}
      logEntries={logEntries}
      page={page}
      onChangePage={(event, newPage) => {
        let variables;
        if (newPage < page) {
          const before = edges[0].cursor;
          variables = {
            before,
            count: rowsPerPage,
          };
        } else {
          const after = edges[logEntries.length - 1].cursor;
          variables = {
            after,
            count: rowsPerPage,
          };
        }
        setPage(newPage);
        fetchMore({
          variables,
          updateQuery: (prev, { fetchMoreResult }) => {
            return fetchMoreResult;
          },
        });
      }}
      onChangeRowsPerPage={(event) => {
        const value = parseInt(event.target.value, 10);
        setRowsPerPage(value);
        setPage(0);
        const variables = {
          count: rowsPerPage,
        };
        fetchMore({
          variables,
          updateQuery: (prev, { fetchMoreResult }) => {
            return fetchMoreResult;
          },
        });
      }}
    />
  );
}
