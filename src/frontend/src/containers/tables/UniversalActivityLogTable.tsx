import type { ReactElement } from 'react';
import { useState } from 'react';
import styled from 'styled-components';
import { ActivityLogTable } from '@components/core/ActivityLogTable/ActivityLogTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from 'src/restgenerated';
import { restQueryKey } from '@utils/queryKeys';
import type { ActivityLogEntry } from '@components/core/ActivityLogTable/types';
import { useQuery } from '@tanstack/react-query';

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
  const { businessAreaSlug } = useBaseUrl();
  const [rowsPerPage, setRowsPerPage] = useState(5);

  const activityLogsParams = {
    businessAreaSlug,
    objectId: objectId,
    limit: rowsPerPage,
    offset: page * rowsPerPage,
  };
  const { data: logsData } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasActivityLogsList,
      activityLogsParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasActivityLogsList(activityLogsParams),
    enabled: !!(businessAreaSlug && objectId),
  });

  const activityLogsCountParams = { businessAreaSlug, objectId };
  const { data: countData } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasActivityLogsCountRetrieve,
      activityLogsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasActivityLogsCountRetrieve(
        activityLogsCountParams,
      ),
    enabled: !!(businessAreaSlug && objectId),
  });

  if (!logsData) {
    return null;
  }

  const logEntries: ActivityLogEntry[] = logsData.results.map(
    (entry, index) => ({
      ...entry,
      id: `${entry.objectId}-${entry.timestamp}-${index}`,
      userDisplayName: entry.user || '',
    }),
  );

  const totalCount = countData?.count ?? 0;

  return (
    <TableWrapper>
      <ActivityLogTable
        totalCount={totalCount}
        rowsPerPage={rowsPerPage}
        logEntries={logEntries}
        page={page}
        onChangePage={(_event, newPage) => {
          setPage(newPage);
        }}
        onChangeRowsPerPage={(event) => {
          const value = parseInt(event.target.value, 10);
          setRowsPerPage(value);
          setPage(0);
        }}
      />
    </TableWrapper>
  );
}
