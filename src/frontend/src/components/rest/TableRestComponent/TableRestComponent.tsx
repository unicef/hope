import {
  EnhancedTableHead,
  HeadCell,
} from '@components/core/Table/EnhancedTableHead';
import { EnhancedTableToolbar } from '@components/core/Table/EnhancedTableToolbar';
import FindInPageIcon from '@mui/icons-material/FindInPage';
import {
  Box as MuiBox,
  Paper as MuiPaper,
  Table as MuiTable,
  TableBody as MuiTableBody,
  TableCell as MuiTableCell,
  TableContainer as MuiTableContainer,
  TableRow as MuiTableRow,
  Skeleton,
  TablePagination,
} from '@mui/material';
import IconButton from '@mui/material/IconButton';
import FirstPageIcon from '@mui/icons-material/FirstPage';
import KeyboardArrowLeft from '@mui/icons-material/KeyboardArrowLeft';
import KeyboardArrowRight from '@mui/icons-material/KeyboardArrowRight';
import LastPageIcon from '@mui/icons-material/LastPage';

function TablePaginationActions(props) {
  const { count, page, rowsPerPage, onPageChange } = props;

  const handleFirstPageButtonClick = (event) => {
    onPageChange(event, 0);
  };

  const handleBackButtonClick = (event) => {
    onPageChange(event, page - 1);
  };

  const handleNextButtonClick = (event) => {
    onPageChange(event, page + 1);
  };

  const handleLastPageButtonClick = (event) => {
    onPageChange(event, Math.max(0, Math.ceil(count / rowsPerPage) - 1));
  };

  return (
    <MuiBox sx={{ flexShrink: 0, ml: 2.5 }}>
      <IconButton
        onClick={handleFirstPageButtonClick}
        disabled={page === 0}
        aria-label="first page"
      >
        <FirstPageIcon />
      </IconButton>
      <IconButton
        onClick={handleBackButtonClick}
        disabled={page === 0}
        aria-label="previous page"
      >
        <KeyboardArrowLeft />
      </IconButton>
      <IconButton
        onClick={handleNextButtonClick}
        disabled={page >= Math.ceil(count / rowsPerPage) - 1}
        aria-label="next page"
      >
        <KeyboardArrowRight />
      </IconButton>
      <IconButton
        onClick={handleLastPageButtonClick}
        disabled={page >= Math.ceil(count / rowsPerPage) - 1}
        aria-label="last page"
      >
        <LastPageIcon />
      </IconButton>
    </MuiBox>
  );
}
import { ReactElement, ChangeEvent, MouseEvent } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

export type Order = 'asc' | 'desc';

const Root = styled('div')`
  width: 100%;
`;

const Paper = styled(MuiPaper)`
  width: 100%;
  margin-bottom: 8px;
  overflow: clip;
`;

const Table = styled(MuiTable)`
  min-width: 750px;
`;

const StyledTableRow = styled(MuiTableRow)`
  height: 70px;
  min-height: 70px;
`;

const StyledTableCell = styled(MuiTableCell)`
  col-span: ${(props) => props.colSpan};

  && {
    white-space: nowrap;
    overflow: auto;
  }
`;

const StyledTableContainer = styled(MuiTableContainer)``;

const StyledBox = styled(MuiBox)`
  display: flex;
  justify-content: space-between;
`;

const StyledTable = styled(Table)`
  aria-labelledby: 'tableTitle';
  size: 'medium';
  aria-label: 'enhanced table';
  data-cy: 'table-title';
`;

const EmptyMessage = styled.div`
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: #a9a9a9;
  font-size: 24px;
  line-height: 28px;
  text-align: center;
  padding: 70px;
`;

const SmallerText = styled(MuiBox)`
  font-size: 16px;
  color: #a9a9a9;
`;

const IconContainer = styled(MuiBox)`
  font-size: 50px;
`;

const Icon = styled(FindInPageIcon)`
  & svg {
    color: #9e9e9e;
  }
`;

interface TableRestComponentProps<T extends { [key: string]: any }> {
  customHeadRenderer?: ReactElement | ((props: any) => ReactElement);
  data: T[];
  renderRow: (row: T) => ReactElement;
  headCells: HeadCell<T>[];
  rowsPerPageOptions: number[];
  rowsPerPage: number;
  page: number;
  itemsCount: number;
  handleChangePage: (event: unknown, newPage: number) => void;
  handleChangeRowsPerPage: (event: ChangeEvent<HTMLInputElement>) => void;
  handleRequestSort: (event: MouseEvent<unknown>, property: string) => void;
  orderBy: string;
  order: Order;
  title?: string;
  loading?: boolean;
  allowSort?: boolean;
  isOnPaper?: boolean;
  actions?: Array<ReactElement>;
  onSelectAllClick?: (event: ChangeEvent<HTMLInputElement>, rows: T[]) => void;
  numSelected?: number;
  hidePagination?: boolean;
  noEmptyMessage?: boolean;
}

export function TableRestComponent<T>({
  title = '',
  renderRow,
  data,
  headCells,
  rowsPerPageOptions,
  rowsPerPage,
  page,
  itemsCount,
  handleChangePage: handleChangePageProp,
  handleChangeRowsPerPage,
  handleRequestSort,
  order,
  orderBy,
  onSelectAllClick,
  loading: loadingProp = false,
  allowSort = true,
  isOnPaper = true,
  actions = [],
  numSelected = 0,
  hidePagination = false,
  customHeadRenderer,
  noEmptyMessage = false,
}: TableRestComponentProps<T>): ReactElement {
  const { t } = useTranslation();

  let emptyRows =
    rowsPerPage - Math.min(rowsPerPage, itemsCount - page * rowsPerPage);
  if (isNaN(emptyRows) || emptyRows < 0) emptyRows = 0;

  let body;

  if (loadingProp) {
    body = Array.from({ length: rowsPerPage }).map((_, index) => (
      <StyledTableRow key={index} data-cy="table-row">
        <StyledTableCell colSpan={headCells.length}>
          <Skeleton variant="rectangular" width="100%" height={70} />
        </StyledTableCell>
      </StyledTableRow>
    ));
  } else if (!data.length) {
    if (noEmptyMessage) {
      body = (
        <StyledTableRow
          data-cy="table-row"
          style={{ height: 70 * emptyRows || 70 }}
        >
          <StyledTableCell colSpan={headCells.length} />
        </StyledTableRow>
      );
    } else {
      body = (
        <StyledTableRow
          data-cy="table-row"
          style={{ height: 70 * emptyRows || 70 }}
        >
          <StyledTableCell colSpan={headCells.length}>
            <EmptyMessage>
              <IconContainer>
                <Icon fontSize="inherit" />
              </IconContainer>
              <MuiBox mt={2}>{t('No results')}</MuiBox>
              <SmallerText mt={2}>
                {t(
                  'Try adjusting your search or your filters to find what you are looking for.',
                )}
              </SmallerText>
            </EmptyMessage>
          </StyledTableCell>
        </StyledTableRow>
      );
    }
  } else {
    body = <>{data.map((row) => renderRow(row))}</>;
  }

  const table = (
    <>
      <StyledTableContainer>
        <StyledBox>
          {title ? <EnhancedTableToolbar title={title} /> : null}
          <StyledBox p={5}>{actions || null}</StyledBox>
        </StyledBox>

        <StyledTable>
          {customHeadRenderer ? (
            typeof customHeadRenderer === 'function' ? (
              customHeadRenderer({
                order,
                headCells,
                orderBy,
                onRequestSort: handleRequestSort,
                rowCount: data.length,
                allowSort,
                onSelectAllClick,
                data,
                numSelected,
              })
            ) : (
              customHeadRenderer
            )
          ) : (
            <EnhancedTableHead<T>
              order={order}
              headCells={headCells}
              orderBy={orderBy}
              onRequestSort={handleRequestSort}
              rowCount={data.length}
              allowSort={allowSort}
              onSelectAllClick={onSelectAllClick}
              data={data}
              numSelected={numSelected}
            />
          )}
          <MuiTableBody>{body}</MuiTableBody>
        </StyledTable>
      </StyledTableContainer>
      {!hidePagination && typeof itemsCount === 'number' && itemsCount >= 0 && (
        <TablePagination
          rowsPerPageOptions={rowsPerPageOptions}
          component="div"
          count={itemsCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePageProp}
          onRowsPerPageChange={handleChangeRowsPerPage}
          ActionsComponent={TablePaginationActions}
          data-cy="table-pagination"
        />
      )}
    </>
  );

  return <Root>{isOnPaper ? <Paper>{table}</Paper> : table}</Root>;
}
