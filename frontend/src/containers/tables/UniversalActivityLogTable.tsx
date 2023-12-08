import React, { ReactElement, useState } from 'react';
import styled from 'styled-components';
import { ActivityLogTable } from '../../components/core/ActivityLogTable/ActivityLogTable';
import { decodeIdString } from '../../utils/utils';
import {
  LogEntryNode,
  useAllLogEntriesQuery,
} from '../../__generated__/graphql';
import { useBaseUrl } from '../../hooks/useBaseUrl';

const TableWrapper = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px;
  padding-bottom: 0;
`;
interface UniversalActivityLogTableProps {
  objectId: string;
}
export function UniversalActivityLogTable({
  objectId,
}: UniversalActivityLogTableProps): ReactElement {
  const [page, setPage] = useState(0);
  const { businessArea } = useBaseUrl();
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const { data, refetch } = useAllLogEntriesQuery({
    variables: {
      businessArea,
      objectId: decodeIdString(objectId),
      first: rowsPerPage,
    },
    fetchPolicy: 'network-only',
  });

  if (!data) {
    return null;
  }
  const { edges } = data.allLogEntries;
  const logEntries = edges.map((edge) => edge.node as LogEntryNode);
  return (
    <TableWrapper>
      <ActivityLogTable
        totalCount={data.allLogEntries.totalCount}
        rowsPerPage={rowsPerPage}
        logEntries={logEntries}
        page={page}
        onChangePage={(event, newPage) => {
          const variables = {
            objectId: decodeIdString(objectId),
            businessArea,
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
            objectId: decodeIdString(objectId),
            businessArea,
            first: rowsPerPage,
            after: undefined,
            last: undefined,
            before: undefined,
          };
          refetch(variables);
        }}
      />
    </TableWrapper>
  );
}
