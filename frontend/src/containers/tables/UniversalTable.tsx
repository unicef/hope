import React, { ReactElement, useState } from 'react';
import useDeepCompareEffect from 'use-deep-compare-effect';
import { LoadingComponent } from '../../components/core/LoadingComponent';
import { HeadCell } from '../../components/core/Table/EnhancedTableHead';
import {
  Order,
  TableComponent,
} from '../../components/core/Table/TableComponent';
import { columnToOrderBy } from '../../utils/utils';

interface UniversalTableProps<T, K> {
  rowsPerPageOptions?: number[];
  initialVariables: K;
  query;
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
}

export function UniversalTable<T, K>({
  rowsPerPageOptions = [5, 10, 15],
  initialVariables,
  query,
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
}: UniversalTableProps<T, K>): ReactElement {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(rowsPerPageOptions[0]);
  const [orderBy, setOrderBy] = useState(defaultOrderBy);
  const [orderDirection, setOrderDirection] = useState<Order>(
    defaultOrderDirection,
  );
  const initVariables = {
    ...initialVariables,
    first: rowsPerPage,
    orderBy: null,
  };
  if (orderBy) {
    initVariables.orderBy = columnToOrderBy(orderBy, orderDirection);
  }
  const { data, refetch, loading, error } = query({
    variables: initVariables,
    notifyOnNetworkStatusChange: true,
    fetchPolicy: 'network-only',
  });

  useDeepCompareEffect(() => {
    if (initialVariables) {
      setPage(0);
    }
  }, [initialVariables]);
  if (error) {
    //  eslint-disable-next-line no-console
    console.error(error);
    return <div>Unexpected error</div>;
  }
  if (!data && loading) return <LoadingComponent />;

  let correctTitle = title;
  if (getTitle) {
    correctTitle = getTitle(data);
  }
  const { edges } = data[queriedObjectName];
  const typedEdges = edges.map((edge) => edge.node as T);

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
      itemsCount={data[queriedObjectName].totalCount}
      handleChangePage={(event, newPage) => {
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
        setPage(newPage);
        refetch(variables);
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
        refetch(variables);
      }}
      handleRequestSort={(event, property) => {
        let direction: Order = 'asc';
        if (property === orderBy) {
          direction = orderDirection === 'asc' ? 'desc' : 'asc';
        }
        setOrderBy(property);
        setOrderDirection(direction);
        setPage(0);
        refetch({
          last: undefined,
          before: undefined,
          after: undefined,
          first: rowsPerPage,
          orderBy: columnToOrderBy(property, direction),
        });
      }}
      orderBy={orderBy}
      order={orderDirection}
      onSelectAllClick={onSelectAllClick}
      numSelected={numSelected}
    />
  );
}
