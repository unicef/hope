import { ReactElement, useState } from 'react';
import useDeepCompareEffect from 'use-deep-compare-effect';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { columnToOrderBy, isPermissionDeniedError } from '@utils/utils';
import { QueryFunction, useQuery } from '@tanstack/react-query';
import {
  Order,
  TableRestComponent,
} from '../TableRestComponent/TableRestComponent';

// TODO MS: add correct types
interface UniversalRestTableProps<T = any, K = any> {
  rowsPerPageOptions?: number[];
  initialVariables: K;
  endpoint: string;
  queriedObjectName: string;
  renderRow: (row: T) => ReactElement;
  headCells: HeadCell<T>[];
  getTitle?: (data: any) => string; // TODO MS: add correct type for data
  title?: string;
  isOnPaper?: boolean;
  defaultOrderBy?: string;
  defaultOrderDirection?: Order;
  actions?: Array<ReactElement>;
  onSelectAllClick?: (event: any, rows: any) => void; // TODO MS: add correct types for event and rows
  numSelected?: number;
  allowSort?: boolean;
  filterOrderBy?: string;
  onPageChanged?: (page: number) => void;
  queryFn: QueryFunction<any, string[], never>;
  queryKey: string[];
}

export const UniversalRestTable = <T, K>({
  rowsPerPageOptions = [5, 10, 15],
  initialVariables,
  renderRow,
  headCells,
  title,
  getTitle,
  isOnPaper,
  actions,
  onSelectAllClick,
  defaultOrderBy,
  defaultOrderDirection = 'asc',
  numSelected = 0,
  allowSort = true,
  queryFn,
  queryKey: initialQueryKey,
}: UniversalRestTableProps<T, K>): ReactElement => {
  const [page, setPage] = useState(0);
  const [queryKey, setQueryKey] = useState(initialQueryKey);
  const [rowsPerPage, setRowsPerPage] = useState(rowsPerPageOptions[0]);
  const [orderBy, setOrderBy] = useState(defaultOrderBy);
  const [orderDirection, setOrderDirection] = useState<Order>(
    defaultOrderDirection,
  );

  const updateQueryKey = (offset: number) => {
    const variables = {
      ...initialVariables,
      offset,
      limit: rowsPerPage,
      orderBy: orderBy ? columnToOrderBy(orderBy, orderDirection) : undefined,
    };
    setQueryKey([queryKey[0], JSON.stringify(variables)]);
  };

  const {
    data,
    refetch,
    isLoading: loading,
    error,
  } = useQuery({ queryKey, queryFn });

  useDeepCompareEffect(() => {
    updateQueryKey(page * rowsPerPage);
  }, [page, rowsPerPage, orderBy, orderDirection]);

  if (error) {
    console.error(error);
    if (isPermissionDeniedError(error)) return <PermissionDenied />;
    return <div>Unexpected error</div>;
  }

  let correctTitle = title;
  if (getTitle) {
    correctTitle = getTitle(data);
  }

  const results = data?.results || [];
  const typedResults = results.map((result) => result as T);

  return (
    <TableRestComponent<T>
      title={correctTitle}
      actions={actions}
      data={typedResults}
      loading={loading}
      renderRow={renderRow}
      isOnPaper={isOnPaper}
      headCells={headCells}
      rowsPerPageOptions={rowsPerPageOptions}
      rowsPerPage={rowsPerPage}
      page={page}
      itemsCount={data?.count ?? 0}
      handleChangePage={(_event, newPage) => {
        setPage(newPage);
        refetch();
      }}
      handleChangeRowsPerPage={(event) => {
        const value = parseInt(event.target.value, 10);
        setRowsPerPage(value);
        setPage(0);
        refetch();
      }}
      handleRequestSort={(_event, property) => {
        const direction: Order =
          orderBy === property && orderDirection === 'asc' ? 'desc' : 'asc';
        setOrderBy(property);
        setOrderDirection(direction);
        setPage(0);
        refetch();
      }}
      orderBy={orderBy}
      order={orderDirection}
      onSelectAllClick={onSelectAllClick}
      numSelected={numSelected}
      allowSort={allowSort}
    />
  );
};
