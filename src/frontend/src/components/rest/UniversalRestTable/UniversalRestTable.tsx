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

interface UniversalRestTableProps<T = any, K = any> {
  page?: number;
  setPage?: (page: number) => void;
  customHeadRenderer?: ReactElement | ((props: any) => ReactElement);
  rowsPerPageOptions?: number[];
  renderRow: (row: T) => ReactElement;
  headCells: HeadCell<T>[];
  getTitle?: (data: any) => string;
  title?: string;
  isOnPaper?: boolean;
  defaultOrderBy?: string;
  defaultOrderDirection?: Order;
  actions?: Array<ReactElement>;
  onSelectAllClick?: (event: any, rows: any) => void;
  numSelected?: number;
  allowSort?: boolean;
  filterOrderBy?: string;
  onPageChanged?: (page: number) => void;
  data: any;
  error;
  isLoading: boolean;
  queryVariables: any;
  setQueryVariables: (variables: K) => void;
  itemsCount?: number;
  initialRowsPerPage?: number;
  hidePagination?: boolean;
  noEmptyMessage?: boolean;
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
  initialRowsPerPage,
  hidePagination,
  customHeadRenderer,
  noEmptyMessage = false,
  page: pageProp,
  setPage: setPageProp,
}: UniversalRestTableProps<T, K>): ReactElement => {
  const [rowsPerPage, setRowsPerPage] = useState(
    initialRowsPerPage || rowsPerPageOptions[0],
  );
  const [orderBy, setOrderBy] = useState(defaultOrderBy);
  const [orderDirection, setOrderDirection] = useState<Order>(
    defaultOrderDirection,
  );

  // Internal page state if not controlled
  const [internalPage, setInternalPage] = useState(0);
  const page = typeof pageProp === 'number' ? pageProp : internalPage;
  const setPage =
    typeof setPageProp === 'function' ? setPageProp : setInternalPage;

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
    if (isPermissionDeniedError(error))
      return <PermissionDenied permission="Permission Denied" />;
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
      itemsCount={itemsCount}
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
      hidePagination={hidePagination}
      customHeadRenderer={customHeadRenderer}
      noEmptyMessage={noEmptyMessage}
    />
  );
};
