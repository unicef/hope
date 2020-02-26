import React, { ReactElement, useState } from 'react';
import styled from 'styled-components';
import {
  LogEntryObject,
  useAllLogEntriesQuery,
  IndividualNode,
} from '../../__generated__/graphql';
import { ActivityLogTable } from '../../components/ActivityLogTable/ActivityLogTable';

interface IndividualsActivityTableProps {
  individual: IndividualNode;
}

const Overview = styled.div`
  margin-top: ${({ theme }) => theme.spacing(6)}px;
`;

export function IndividualActivityTable({
  individual,
}: IndividualsActivityTableProps): ReactElement {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const { data, fetchMore } = useAllLogEntriesQuery({
    variables: {
      objectId: individual.id,
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
    <Overview>
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
    </Overview>
  );
}
