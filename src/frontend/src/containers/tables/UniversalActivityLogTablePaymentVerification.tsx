import { ReactElement, useState } from 'react';
import { ActivityLogTablePaymentVerification } from '@components/core/ActivityLogTablePaymentVerification/ActivityLogTablePaymentVerification';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/index';
import { useQuery } from '@tanstack/react-query';

interface UniversalActivityLogTablePaymentVerificationProps {
  objectId: string;
}
export function UniversalActivityLogTablePaymentVerification({
  objectId,
}: UniversalActivityLogTablePaymentVerificationProps): ReactElement {
  const [page, setPage] = useState(0);
  const { businessAreaSlug } = useBaseUrl();
  const [rowsPerPage, setRowsPerPage] = useState(5);

  const { data: logData } = useQuery({
    queryKey: ['activityLogs', businessAreaSlug, objectId, page, rowsPerPage],
    queryFn: () =>
      RestService.restBusinessAreasActivityLogsList({
        businessAreaSlug,
        objectId: objectId,
        limit: rowsPerPage,
        offset: page * rowsPerPage,
      }),
    enabled: !!(businessAreaSlug && objectId),
  });

  const { data: countData } = useQuery({
    queryKey: ['activityLogsCount', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasActivityLogsCountRetrieve({
        businessAreaSlug,
      }),
    enabled: !!businessAreaSlug,
  });

  if (!logData || !countData) {
    return null;
  }
  const logEntries = logData?.results;
  const totalCount = countData.count;
  return (
    <ActivityLogTablePaymentVerification
      totalCount={totalCount}
      rowsPerPage={rowsPerPage}
      logEntries={logEntries}
      page={page}
      onChangePage={(_, newPage) => {
        setPage(newPage);
      }}
      onChangeRowsPerPage={(event) => {
        const value = parseInt(event.target.value, 10);
        setRowsPerPage(value);
        setPage(0);
      }}
    />
  );
}
