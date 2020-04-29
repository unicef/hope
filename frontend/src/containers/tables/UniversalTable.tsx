import React, { ReactElement, useState, useEffect } from 'react';
import { Order, TableComponent } from '../../components/table/TableComponent';
import { HeadCell } from '../../components/table/EnhancedTableHead';
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
}: UniversalTableProps<T, K>): ReactElement {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(rowsPerPageOptions[0]);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');
  const { data, refetch, loading, error } = query({
    variables: { ...initialVariables, first: rowsPerPage },
    fetchPolicy: 'network-only',
  });
  console.log('error', error)

  useEffect(() => {
    if (initialVariables) {
      setPage(0);
    }
  }, [initialVariables]);

  if (!data) {
    return null;
  }

  let correctTitle = title;
  if (getTitle) {
    correctTitle = getTitle(data);
  }
  const { edges } = data[queriedObjectName];
  const typedEdges = edges.map((edge) => edge.node as T);
  //eslint-disable-next-line
  
  return (
    <TableComponent<T>
      title={correctTitle}
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
        let direction = 'asc';
        if (property === orderBy) {
          direction = orderDirection === 'asc' ? 'desc' : 'asc';
        }
        setOrderBy(property);
        setOrderDirection(direction);
        refetch({
          last: undefined,
          before: undefined,
          after: undefined,
          first: rowsPerPage,
          orderBy: columnToOrderBy(property, direction),
        });
      }}
      orderBy={orderBy}
      order={orderDirection as Order}
    />
  );
}
