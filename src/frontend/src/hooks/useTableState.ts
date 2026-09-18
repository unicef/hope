import type { Order } from '@components/rest/TableRestComponent/TableRestComponent';
import { columnToOrderBy } from '@utils/utils';
import { useCallback, useMemo, useState } from 'react';

export interface UseTableStateOptions {
  rowsPerPageOptions?: number[];
  initialRowsPerPage?: number;
  // Column shown as active in the table header on first render.
  defaultOrderBy?: string;
  defaultOrderDirection?: Order;
  // Raw `ordering` query value used while no column sort is active.
  defaultOrdering?: string;
  // Page goes back to 0 whenever this (memoized) value changes.
  resetPageOn?: unknown;
}

export interface PaginationParams {
  limit: number;
  offset: number;
  ordering?: string;
}

export interface TableState {
  page: number;
  rowsPerPage: number;
  rowsPerPageOptions: number[];
  orderBy?: string;
  orderDirection: Order;
  ordering?: string;
  limit: number;
  offset: number;
  paginationParams: PaginationParams;
  setPage: (page: number) => void;
  setRowsPerPage: (rowsPerPage: number) => void;
  requestSort: (column: string) => void;
}

const DEFAULT_ROWS_PER_PAGE_OPTIONS = [5, 10, 15];

// Single owner of a table's pagination and sort state. Everything the API
// needs (`ordering`, `limit`, `offset`) is derived during render, so a parent
// can build its query key in the same render and never fires a request for
// an intermediate state.
export function useTableState({
  rowsPerPageOptions = DEFAULT_ROWS_PER_PAGE_OPTIONS,
  initialRowsPerPage,
  defaultOrderBy,
  defaultOrderDirection = 'asc',
  defaultOrdering,
  resetPageOn,
}: UseTableStateOptions = {}): TableState {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPageState] = useState(
    initialRowsPerPage ?? rowsPerPageOptions[0],
  );
  const [orderBy, setOrderBy] = useState(defaultOrderBy);
  const [orderDirection, setOrderDirection] = useState<Order>(
    defaultOrderDirection,
  );

  // Reset the page while rendering (not in an effect): React re-renders
  // immediately with page 0 before committing, so no query goes out with a
  // stale offset.
  const [prevResetPageOn, setPrevResetPageOn] = useState(resetPageOn);
  if (prevResetPageOn !== resetPageOn) {
    setPrevResetPageOn(resetPageOn);
    setPage(0);
  }

  const setRowsPerPage = useCallback((value: number) => {
    setRowsPerPageState(value);
    setPage(0);
  }, []);

  const requestSort = useCallback(
    (column: string) => {
      const direction: Order =
        orderBy === column && orderDirection === 'asc' ? 'desc' : 'asc';
      setOrderBy(column);
      setOrderDirection(direction);
      setPage(0);
    },
    [orderBy, orderDirection],
  );

  const ordering = orderBy
    ? columnToOrderBy(orderBy, orderDirection)
    : defaultOrdering;
  const limit = rowsPerPage;
  const offset = page * rowsPerPage;

  const paginationParams = useMemo<PaginationParams>(
    () => ({ limit, offset, ...(ordering ? { ordering } : {}) }),
    [limit, offset, ordering],
  );

  return {
    page,
    rowsPerPage,
    rowsPerPageOptions,
    orderBy,
    orderDirection,
    ordering,
    limit,
    offset,
    paginationParams,
    setPage,
    setRowsPerPage,
    requestSort,
  };
}
