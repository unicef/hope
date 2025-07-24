import { ReactElement, useEffect, useMemo, useState } from 'react';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import {
  columnToOrderBy,
  filterEmptyParams,
  isPermissionDeniedError,
} from '@utils/utils';
import {
  Order,
  TableRestComponent,
} from '../TableRestComponent/TableRestComponent';
import { isEqual } from 'lodash';

//TODO MS: add correct types
interface UniversalRestTableProps<T = any, K = any> {
  rowsPerPageOptions?: number[];
  renderRow: (row: T) => ReactElement;
  headCells: HeadCell<T>[];
  getTitle?: (data: any) => string; //TODO MS: add correct type for data
  title?: string;
  isOnPaper?: boolean;
  defaultOrderBy?: string;
  defaultOrderDirection?: Order;
  actions?: Array<ReactElement>;
  onSelectAllClick?: (event: any, rows: any) => void; //TODO MS: add correct types for event and rows
  numSelected?: number;
  allowSort?: boolean;
  filterOrderBy?: string;
  onPageChanged?: (page: number) => void;
  //TODO MS: add correct types
  data: any;
  error;
  isLoading: boolean;
  queryVariables: any;
  setQueryVariables: (variables: K) => void;
  itemsCount?: number;
}
type QueryVariables = {
  offset: number;
  limit: number;
  ordering?: string;
};

export const UniversalRestTable = <T, K>({
  rowsPerPageOptions = [5, 10, 15],
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
  data,
  error,
  isLoading,
  queryVariables,
  setQueryVariables,
  itemsCount,
}: UniversalRestTableProps<T, K>): ReactElement => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(rowsPerPageOptions[0]);
  const [orderBy, setOrderBy] = useState(defaultOrderBy);
  const [orderDirection, setOrderDirection] = useState<Order>(
    defaultOrderDirection,
  );

  const filteredQueryVariables = useMemo(() => {
    const filtered = filterEmptyParams(queryVariables);
    return {
      ...filtered,
      businessAreaSlug: queryVariables.businessAreaSlug,
      ...(queryVariables.ordering ? { ordering: queryVariables.ordering } : {}),
    };
  }, [queryVariables]);

  useEffect(() => {
    const newVariables: QueryVariables = {
      ...filteredQueryVariables,
      offset: page * rowsPerPage,
      limit: rowsPerPage,
    };

    const ordering = orderBy
      ? columnToOrderBy(orderBy, orderDirection)
      : filteredQueryVariables.ordering;

    if (ordering) {
      newVariables.ordering = ordering;
    }

    const newState = newVariables as unknown as K;

    if (!isEqual(newState, queryVariables)) {
      setQueryVariables(newState);
    }
  }, [
    page,
    rowsPerPage,
    orderBy,
    orderDirection,
    filteredQueryVariables,
    setQueryVariables,
    queryVariables,
  ]);

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
      data-cy="universal-rest-table"
      title={correctTitle}
      actions={actions}
      data={typedResults}
      loading={isLoading}
      renderRow={renderRow}
      isOnPaper={isOnPaper}
      headCells={headCells}
      rowsPerPageOptions={rowsPerPageOptions}
      rowsPerPage={rowsPerPage}
      page={page}
      itemsCount={itemsCount ?? 0}
      handleChangePage={(_event, newPage) => {
        setPage(newPage);
      }}
      handleChangeRowsPerPage={(event) => {
        const value = parseInt(event.target.value, 10);
        setRowsPerPage(value);
        setPage(0);
      }}
      handleRequestSort={(_event, property) => {
        const direction: Order =
          orderBy === property && orderDirection === 'asc' ? 'desc' : 'asc';
        setOrderBy(property);
        setOrderDirection(direction);
        setPage(0);
      }}
      orderBy={orderBy}
      order={orderDirection}
      onSelectAllClick={onSelectAllClick}
      numSelected={numSelected}
      allowSort={allowSort}
    />
  );
};
