import React, { ReactElement, useState } from 'react';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import {
  AllCashPlansQueryVariables,
  AllLogEntriesQuery,
  AllLogEntriesQueryVariables,
  AllPaymentRecordsQueryVariables,
  CashPlanNode,
  LogEntryAction,
  LogEntryObject,
  ProgramNode,
  useAllLogEntriesQuery,
} from '../__generated__/graphql';
import { Order, TableComponent } from '../components/table/TableComponent';
import { HeadCell } from '../components/table/EnhancedTableHead';
import { columnToOrderBy } from '../utils/utils';
import { useBusinessArea } from '../hooks/useBusinessArea';
import moment from 'moment';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import Collapse from '@material-ui/core/Collapse';
import { IconButton, makeStyles, Paper } from '@material-ui/core';
import { MiśTheme } from '../theme';
import clsx from 'clsx';
import TableContainer from '@material-ui/core/TableContainer';
import TablePagination from '@material-ui/core/TablePagination';

const headCells: HeadCell<CashPlanNode>[] = [
  {
    disablePadding: false,
    label: 'Date',
    id: 'timestamp',
    numeric: false,
    weight: 0.4,
  },
  {
    disablePadding: false,
    label: 'User',
    id: 'actor',
    numeric: false,
    weight: 0.6,
  },
  {
    disablePadding: false,
    label: 'Action',
    id: 'action',
    numeric: false,
    weight: 0.4,
  },
  {
    disablePadding: false,
    label: 'Change from',
    id: 'change_from',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Change to',
    id: 'change_to',
    numeric: false,
  },
];

const StatusContainer = styled.div`
  width: 120px;
`;
const ButtonPlaceHolder = styled.div`
  width: 48px;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const Table = styled.div`
  display: flex;
  flex-direction: column;
`;
const Row = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  cursor: ${({ hover }) => (!hover ? 'auto' : 'pointer')};
  &:hover {
    background-color: ${({ hover }) => (!hover ? 'transparent' : '#e8e8e8')};
  }
`;
const Cell = styled.div`
  display: flex;
  flex: ${({ weight }) => weight || 1};

  padding: 16px;
  font-size: 0.875rem;
  text-align: left;
  line-height: 1.43;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
  letter-spacing: 0.01071em;
  vertical-align: inherit;
`;
const HeadingCell = styled.div`
  display: flex;
  flex: ${({ weight }) => weight || 1};

  padding: 16px;
  font-size: 0.875rem;
  text-align: left;
  font-weight: 500;
  line-height: 1.43;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
  letter-spacing: 0.01071em;
  vertical-align: inherit;
`;
const PaperContainer = styled(Paper)`
  width: 100%;
  padding: ${({ theme }) => theme.spacing(5)}px 0;
  margin-bottom: ${({ theme }) => theme.spacing(5)}px;
`;
const ButtonContainer = styled.div`
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const CollapseContainer = styled(Collapse)`
  background-color: #e8e8e8;
`;

const useStyles = makeStyles((theme: MiśTheme) => ({
  expanded: {},
  expandIcon: {
    transform: 'rotate(0deg)',
    transition: theme.transitions.create('transform', { duration: 400 }),
    '&:hover': {
      // Disable the hover effect for the IconButton,
      // because a hover effect should apply to the entire Expand button and
      // not only to the IconButton.
      backgroundColor: 'transparent',
    },
    '&$expanded': {
      transform: 'rotate(180deg)',
    },
  },
}));

interface LogRowProps {
  logEntry: LogEntryObject;
}

function LogRow({ logEntry }: LogRowProps): ReactElement {
  const changes = JSON.parse(logEntry.changesDisplayDict);
  const [expanded, setExpanded] = useState(false);
  const classes = useStyles({});
  const keys = Object.keys(changes);
  const { length } = keys;
  if (length === 1) {
    return (
      <Row role='checkbox'>
        <Cell weight={headCells[0].weight}>
          {moment(logEntry.timestamp).format('DD MMM YYYY HH:mm')}
        </Cell>
        <Cell weight={headCells[1].weight}>
          {logEntry.actor
            ? `${logEntry.actor.firstName} ${logEntry.actor.lastName}`
            : null}
        </Cell>
        <Cell weight={headCells[2].weight}>{keys[0].toUpperCase()}</Cell>
        <Cell weight={headCells[3].weight}>{changes[keys[0]][0]}</Cell>
        <Cell weight={headCells[4].weight}>{changes[keys[0]][1]}</Cell>
        <ButtonPlaceHolder />
      </Row>
    );
  }
  return (
    <>
      <Row onClick={() => setExpanded(!expanded)} hover>
        <Cell weight={headCells[0].weight}>
          {moment(logEntry.timestamp).format('DD MMM YYYY HH:mm')}
        </Cell>
        <Cell weight={headCells[1].weight}>
          {logEntry.actor
            ? `${logEntry.actor.firstName} ${logEntry.actor.lastName}`
            : null}
        </Cell>
        <Cell weight={headCells[2].weight}>Multiple</Cell>
        <Cell weight={headCells[3].weight} />
        <Cell weight={headCells[4].weight} />
        <ButtonContainer>
          <IconButton
            className={clsx(classes.expandIcon, {
              [classes.expanded]: expanded,
            })}
            onClick={() => setExpanded(!expanded)}
          >
            <ExpandMore />
          </IconButton>
        </ButtonContainer>
      </Row>

      <CollapseContainer in={expanded}>
        {keys.map((key) => {
          return (
            <Row>
              <Cell weight={headCells[0].weight} />
              <Cell weight={headCells[1].weight} />
              <Cell weight={headCells[2].weight}>{key}</Cell>
              <Cell weight={headCells[3].weight}>{changes[key][0]}</Cell>
              <Cell weight={headCells[4].weight}>{changes[key][1]}</Cell>
              <ButtonPlaceHolder />
            </Row>
          );
        })}
      </CollapseContainer>
    </>
  );
}
interface ProgramActivityLogTableProps {
  program: ProgramNode;
}
export function ProgramActivityLogTable({
  program,
}: ProgramActivityLogTableProps): ReactElement {
  const history = useHistory();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');
  const businessArea = useBusinessArea();
  const { data, fetchMore } = useAllLogEntriesQuery({
    variables: {
      objectId: program.id,
      count: rowsPerPage,
    },
    fetchPolicy: 'network-only',
  });
  if (!data) {
    return null;
  }
  const { edges } = data.allLogEntries;
  const cashPlans = edges.map((edge) => edge.node as LogEntryObject);
  console.log('activity log', cashPlans);
  return (
    <PaperContainer>
      <Table>
        <Row>
          {headCells.map((item) => {
            return (
              <HeadingCell style={{ flex: item.weight || 1 }}>
                {item.label}
              </HeadingCell>
            );
          })}
          <ButtonPlaceHolder />
        </Row>
        {cashPlans.map((value) => (
          <LogRow logEntry={value} />
        ))}
      </Table>
      <TablePagination
        rowsPerPageOptions={[5, 10, 15]}
        component='div'
        count={data.allLogEntries.totalCount}
        rowsPerPage={rowsPerPage}
        page={page}
        onChangePage={(event, newPage) => {
          let variables;
          if (newPage < page) {
            const before = edges[0].cursor;
            variables = {
              before,
              count: rowsPerPage,
            };
          } else {
            const after = edges[cashPlans.length - 1].cursor;
            variables = {
              after,
              count: rowsPerPage,
            };
          }
          setPage(newPage);
          fetchMore({
            variables,
            updateQuery: (prev, { fetchMoreResult }) => {
              return fetchMoreResult;
            },
          });
        }}
        onChangeRowsPerPage={(event) => {
          const value = parseInt(event.target.value, 10);
          setRowsPerPage(value);
          setPage(0);
          const variables = {
            count: rowsPerPage,
          };
          fetchMore({
            variables,
            updateQuery: (prev, { fetchMoreResult }) => {
              return fetchMoreResult;
            },
          });
        }}
      />
    </PaperContainer>
  );
}
