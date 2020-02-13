import React, { ReactElement, useState } from 'react';
import styled from 'styled-components';
import ExpandLess from '@material-ui/icons/ExpandLessRounded';
import ExpandMore from '@material-ui/icons/ExpandMoreRounded';
import Collapse from '@material-ui/core/Collapse';
import { Paper } from '@material-ui/core';
import TablePagination from '@material-ui/core/TablePagination';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import { LogEntryObject } from '../../__generated__/graphql';
import { LogRow } from './LogRow';
import { ButtonPlaceHolder, Row } from './TableStyledComponents';
import { headCells } from './headCels';

const Table = styled.div`
  display: flex;
  flex-direction: column;
`;
const HeadingCell = styled.div`
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
const PaperContainer = styled(Paper)`
  width: 100%;
  padding: ${({ theme }) => theme.spacing(5)}px 0;
  margin-bottom: ${({ theme }) => theme.spacing(5)}px;
`;
const Toolbar = styled.div`
  margin: 0 ${({ theme }) => theme.spacing(6)}px;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
`;

interface ActivityLogTableProps {
  logEntries: LogEntryObject[];
  totalCount: number;
  rowsPerPage: number;
  page: number;
  onChangePage: (event: unknown, newPage: number) => void;
  onChangeRowsPerPage: (event: React.ChangeEvent<HTMLInputElement>) => void;
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
  return (
    <PaperContainer>
      <Toolbar>
        <Typography variant='h6'>Activity Log</Typography>
        <Button
          variant='outlined'
          color='primary'
          endIcon={expanded ? <ExpandLess /> : <ExpandMore />}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? 'HIDE' : 'SHOW'}
        </Button>
      </Toolbar>
      <Collapse in={expanded}>
        <Table>
          <Row>
            {headCells.map((item) => {
              return (
                <HeadingCell key={item.id} style={{ flex: item.weight || 1 }}>
                  {item.label}
                </HeadingCell>
              );
            })}
            <ButtonPlaceHolder />
          </Row>
          {logEntries.map((value) => (
            <LogRow key={value.id} logEntry={value} />
          ))}
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 15]}
          component='div'
          count={totalCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onChangePage={onChangePage}
          onChangeRowsPerPage={onChangeRowsPerPage}
        />
      </Collapse>
    </PaperContainer>
  );
}
