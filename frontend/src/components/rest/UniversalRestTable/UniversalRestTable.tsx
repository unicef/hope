import { ReactElement, useState } from 'react';
import useDeepCompareEffect from 'use-deep-compare-effect';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { Order, TableComponent } from '@components/core/Table/TableComponent';
import { columnToOrderBy, isPermissionDeniedError } from '@utils/utils';
import { QueryFunction, useQuery } from '@tanstack/react-query';

interface UniversalRestTableProps<T, K> {
  rowsPerPageOptions?: number[];
  initialVariables: K;
  endpoint: string;
  queriedObjectName: string;
  renderRow: (row: T) => ReactElement;
  headCells: HeadCell<T>[];
  getTitle?: (data) => string;
  title?: string;
  isOnPaper?: boolean;
  defaultOrderBy?: string;
  defaultOrderDirection?: Order;
  actions?: Array<ReactElement>;
  onSelectAllClick?: (event, rows) => void;
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
  queriedObjectName,
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
  filterOrderBy,
  onPageChanged,
  queryFn,
  queryKey: initialQueryKey,
}: UniversalRestTableProps<T, K>): ReactElement => {
  const [page, _setPage] = useState(0);
  const [queryKey, setQueryKey] = useState(initialQueryKey);
  const [rowsPerPage, setRowsPerPage] = useState(rowsPerPageOptions[0]);
  const [orderBy, setOrderBy] = useState(defaultOrderBy);
  const [orderDirection, setOrderDirection] = useState<Order>(
    defaultOrderDirection,
  );

  const setPage = (newPage: number): void => {
    _setPage(newPage);
    if (onPageChanged) {
      onPageChanged(newPage);
    }
  };

  const initVariables = {
    ...initialVariables,
    first: rowsPerPage,
    orderBy: null,
  };

  if (orderBy && !filterOrderBy && allowSort) {
    initVariables.orderBy = columnToOrderBy(orderBy, orderDirection);
  }
  if (filterOrderBy) {
    initVariables.orderBy = filterOrderBy;
  }

  setQueryKey([queryKey[1], JSON.stringify(initVariables)]);

  const {
    data,
    refetch,
    isLoading: loading,
    error,
  } = useQuery({ queryKey, queryFn });

  useDeepCompareEffect(() => {
    if (initialVariables) {
      setPage(0);
    }
  }, [initialVariables]);
  if (error) {
    //  eslint-disable-next-line no-console
    console.error(error);
    if (isPermissionDeniedError(error)) return <PermissionDenied />;

    return <div>Unexpected error</div>;
  }

  let correctTitle = title;
  if (getTitle) {
    correctTitle = getTitle(data);
  }
  const edges = data?.[queriedObjectName] || [];
  const typedEdges = edges.map((edge) => edge as T);

  return (
    <TableComponent<T>
      title={correctTitle}
      actions={actions}
      data={typedEdges}
      loading={loading}
      renderRow={renderRow}
      isOnPaper={isOnPaper}
      headCells={headCells}
      rowsPerPageOptions={rowsPerPageOptions}
      rowsPerPage={rowsPerPage}
      page={page}
      itemsCount={data?.[queriedObjectName]?.totalCount ?? 0}
      handleChangePage={(_event, newPage) => {
        if (!edges.length) return;
        const variables = {
          first: undefined,
          last: undefined,
          after: undefined,
          before: undefined,
          orderBy: undefined,
        };
        if (newPage < page) {
          variables.last = rowsPerPage;
          variables.before = edges[0].cursor;
        } else {
          variables.after = edges[edges.length - 1].cursor;
          variables.first = rowsPerPage;
        }

        if (orderBy) {
          variables.orderBy = columnToOrderBy(orderBy, orderDirection);
        }
        if (filterOrderBy) {
          variables.orderBy = columnToOrderBy(filterOrderBy, orderDirection);
        }

        setQueryKey([queryKey[1], JSON.stringify(initVariables)]);

        setPage(newPage);
        refetch();
      }}
      handleChangeRowsPerPage={(event) => {
        const value = parseInt(event.target.value, 10);
        setRowsPerPage(value);
        setPage(0);
        const variables = {
          ...initialVariables,
          first: value,
          last: undefined,
          before: undefined,
          after: undefined,
          orderBy: undefined,
        };
        if (orderBy) {
          variables.orderBy = columnToOrderBy(orderBy, orderDirection);
        }
        setQueryKey([queryKey[1], JSON.stringify(variables)]);
        refetch();
      }}
      handleRequestSort={(_event, property) => {
        let direction: Order = 'asc';
        if (property === orderBy) {
          direction = orderDirection === 'asc' ? 'desc' : 'asc';
        }
        setOrderBy(property);
        setOrderDirection(direction);
        setPage(0);
        const variables = {
          last: undefined,
          before: undefined,
          after: undefined,
          first: rowsPerPage,
          orderBy: columnToOrderBy(property, direction),
        };
        setQueryKey([queryKey[1], JSON.stringify(variables)]);
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
