import { Paper, styled } from '@mui/material';
import Button from '@mui/material/Button';
import Collapse from '@mui/material/Collapse';
import TablePagination from '@mui/material/TablePagination';
import Typography from '@mui/material/Typography';
import ExpandLessIcon from '@mui/icons-material/ExpandLessRounded';
import ExpandMoreIcon from '@mui/icons-material/ExpandMoreRounded';
import { ChangeEvent, ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ActivityLogEntry } from './types';
import { headCells } from './headCells';
import { LogRow } from './LogRow';
import { ButtonPlaceHolder, Row } from './TableStyledComponents';

const Table = styled('div')`
  display: flex;
  flex-direction: column;
`;

interface HeadingCellProps {
  weight?: number;
}

const HeadingCell = styled('div')<HeadingCellProps>`
  display: flex;
  flex: ${({ weight }) => weight || 1};
  padding: 16px;
  font-size: 12px;
  text-align: left;
  font-weight: 500;
  line-height: 1.43rem;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
  letter-spacing: 0.01071em;
  vertical-align: inherit;
`;
const PaperContainer = styled(Paper)(() => ({
  width: '100%',
  padding: '20px 0',
  marginBottom: '20px',
}));

const Toolbar = styled('div')(() => ({
  margin: '0 24px',
  display: 'flex',
  flexDirection: 'row',
  justifyContent: 'space-between',
}));

interface ActivityLogTableProps {
  logEntries: ActivityLogEntry[];
  totalCount: number;
  rowsPerPage: number;
  page: number;
  onChangePage: (event: unknown, newPage: number) => void;
  onChangeRowsPerPage: (event: ChangeEvent<HTMLInputElement>) => void;
}
export function ActivityLogTable({
  logEntries,
  totalCount,
  rowsPerPage,
  page,
  onChangePage,
  onChangeRowsPerPage,
}: ActivityLogTableProps): ReactElement {
  const [expanded, setExpanded] = useState(false);
  const { t } = useTranslation();

  return (
    <PaperContainer data-cy="activity-log-container">
      <Toolbar>
        <Typography variant="h6" data-cy="activity-log-title">
          {t('Activity Log')}
        </Typography>
        <Button
          variant="outlined"
          color="primary"
          endIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          onClick={() => setExpanded(!expanded)}
          data-cy="expand-collapse-button"
        >
          {expanded ? 'HIDE' : 'SHOW'}
        </Button>
      </Toolbar>
      <Collapse in={expanded}>
        <Table data-cy="activity-log-table">
          <Row>
            {headCells.map((item) => (
              <HeadingCell
                data-cy={`heading-cell-${item.id}`}
                key={item.id}
                style={{ flex: item.weight || 1 }}
              >
                {item.label}
              </HeadingCell>
            ))}
            <ButtonPlaceHolder />
          </Row>
          {logEntries.map((value) => (
            <LogRow data-cy="log-row" key={value.id} logEntry={value} />
          ))}
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 15]}
          component="div"
          data-cy="pagination"
          count={totalCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={onChangePage}
          onRowsPerPageChange={onChangeRowsPerPage}
        />
      </Collapse>
    </PaperContainer>
  );
}
