import type { ReactElement } from 'react';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import type { TableState } from '@hooks/useTableState';
import type { HeadCell } from '@core/Table/EnhancedTableHead';
import { isUndefined, omitBy } from 'lodash';
import { restQueryKey } from '@utils/queryKeys';

interface UniversalRestQueryTableProps<T = any> {
  tableState: TableState;
  renderRow: (row: T) => ReactElement;
  headCells: HeadCell<T>[];
  getTitle?: (data: any) => string;
  title?: string;
  isOnPaper?: boolean;
  actions?: Array<ReactElement>;
  onSelectAllClick?: (event: any, rows: any) => void;
  numSelected?: number;
  allowSort?: boolean;
  filterVariables: any;
  itemsCount?: number;
  query: (variables: any) => Promise<any>;
  customEnabled?: boolean;
}

export function UniversalRestQueryTable<T>(
  props: UniversalRestQueryTableProps,
): ReactElement {
  const {
    query,
    filterVariables,
    tableState,
    customEnabled = true,
    ...propsToPass
  } = props;
  const { businessArea, programCode } = useBaseUrl();
  const queryVariables = {
    ...omitBy(filterVariables, isUndefined),
    ...tableState.paginationParams,
  };
  const { data, isLoading, error } = useQuery({
    queryKey: restQueryKey(query, {
      ...queryVariables,
      programCode,
      businessArea,
    }),
    queryFn: () =>
      query({
        businessAreaSlug: businessArea,
        programCode,
        ...queryVariables,
      }),
    enabled: customEnabled && !!businessArea && !!programCode,
  });
  return (
    <UniversalRestTable<T>
      {...propsToPass}
      tableState={tableState}
      data={data}
      isLoading={isLoading}
      error={error}
    />
  );
}
