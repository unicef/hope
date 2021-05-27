import React, {ReactElement, useState} from 'react';
import styled from 'styled-components';
import Collapse from '@material-ui/core/Collapse';
import {Paper} from '@material-ui/core';
import TablePagination from '@material-ui/core/TablePagination';
import {AllLogEntriesQuery, LogEntryNode,} from '../../../__generated__/graphql';
import {ButtonPlaceHolder, Row,} from '../../../components/ActivityLogTable/TableStyledComponents';
import {useArrayToDict} from '../../../hooks/useArrayToDict';
import {MainActivityLogTableRow} from './MainActivityLogTableRow';
import {headCells} from './MainActivityLogTableHeadCells';

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

interface MainActivityLogTableProps {
  logEntries: LogEntryNode[];
  totalCount: number;
  rowsPerPage: number;
  page: number;
  onChangePage: (event: unknown, newPage: number) => void;
  onChangeRowsPerPage: (event: React.ChangeEvent<HTMLInputElement>) => void;
  actionChoices: AllLogEntriesQuery['logEntryActionChoices'];
  loading: boolean;
}
export function MainActivityLogTable({
  logEntries,
  totalCount,
  rowsPerPage,
  page,
  onChangePage,
  onChangeRowsPerPage,
  actionChoices,
  loading = false,
}: MainActivityLogTableProps): ReactElement {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [expanded, setExpanded] = useState(true);
  const choicesDict = useArrayToDict(actionChoices, 'value', 'name');
  return (
    <PaperContainer>
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
            <MainActivityLogTableRow
              key={value.id}
              actionChoicesDict={choicesDict}
              logEntry={
                value as AllLogEntriesQuery['allLogEntries']['edges'][number]['node']
              }
            />
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
          backIconButtonProps={{ ...(loading && { disabled: true }) }}
          nextIconButtonProps={{ ...(loading && { disabled: true }) }}
        />
      </Collapse>
    </PaperContainer>
  );
}
