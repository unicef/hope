import type { ReactElement } from 'react';
import { PermissionDenied } from '@components/core/PermissionDenied';
import type { HeadCell } from '@components/core/Table/EnhancedTableHead';
import type { TableState } from '@hooks/useTableState';
import { isPermissionDeniedError } from '@utils/utils';
import { TableRestComponent } from '../TableRestComponent/TableRestComponent';

interface UniversalRestTableProps<T = any> {
  tableState: TableState;
  customHeadRenderer?: ReactElement | ((props: any) => ReactElement);
  renderRow: (row: T) => ReactElement;
  headCells: HeadCell<T>[];
  getTitle?: (data: any) => string;
  title?: string;
  isOnPaper?: boolean;
  actions?: Array<ReactElement>;
  onSelectAllClick?: (event: any, rows: any) => void;
  numSelected?: number;
  allowSort?: boolean;
  data: any;
  error;
  isLoading: boolean;
  isFetching?: boolean;
  itemsCount?: number;
  hidePagination?: boolean;
  noEmptyMessage?: boolean;
}

// Stateless view: pagination and sort live in the caller's `useTableState`,
// so the caller builds its query key from the same state in the same render.
export function UniversalRestTable<T>({
  tableState,
  renderRow,
  headCells,
  title,
  getTitle,
  isOnPaper,
  actions,
  onSelectAllClick,
  numSelected = 0,
  allowSort = true,
  data,
  error,
  isLoading,
  isFetching,
  itemsCount,
  hidePagination,
  customHeadRenderer,
  noEmptyMessage = false,
}: UniversalRestTableProps<T>): ReactElement {
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
      isFetching={isFetching}
      renderRow={renderRow}
      isOnPaper={isOnPaper}
      headCells={headCells}
      rowsPerPageOptions={tableState.rowsPerPageOptions}
      rowsPerPage={tableState.rowsPerPage}
      page={tableState.page}
      itemsCount={itemsCount}
      handleChangePage={(_event, newPage) => {
        tableState.setPage(newPage);
      }}
      handleChangeRowsPerPage={(event) => {
        tableState.setRowsPerPage(parseInt(event.target.value, 10));
      }}
      handleRequestSort={(_event, property) => {
        // `property` widens to `keyof T` for typed head cells; the ordering key
        // goes out as a query-string param, so pass it on as a string.
        tableState.requestSort(String(property));
      }}
      orderBy={tableState.orderBy}
      order={tableState.orderDirection}
      onSelectAllClick={onSelectAllClick}
      numSelected={numSelected}
      allowSort={allowSort}
      hidePagination={hidePagination}
      customHeadRenderer={customHeadRenderer}
      noEmptyMessage={noEmptyMessage}
    />
  );
}
