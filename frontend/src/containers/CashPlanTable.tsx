import React, { ReactElement, useState } from 'react';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import Moment from 'react-moment';
import {
  CashPlanNode,
  ProgramNode,
  useAllCashPlansQuery,
} from '../__generated__/graphql';
import { TableComponent } from '../components/table/TableComponent';
import { HeadCell } from '../components/table/EnhancedTableHead';
import { StatusBox } from '../components/StatusBox';
import { cashPlanStatusToColor } from '../utils/utils';

const headCells: HeadCell<CashPlanNode>[] = [
  {
    disablePadding: false,
    label: 'Cash Plan ID',
    id: 'cashAssistId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'No. of Households',
    id: 'numberOfHouseholds',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Currency',
    id: 'currency',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Total Entitled Quantity',
    id: 'totalEntitledQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Delivered Quantity',
    id: 'totalDeliveredQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Undelivered Quantity',
    id: 'totalUndeliveredQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Dispersion Date',
    id: 'disbursementDate',
    numeric: false,
  },
];
const StatusContainer = styled.div`
  width: 120px;
`;

interface CashPlanTableProps {
  program: ProgramNode;
}
export function CashPlanTable({ program }: CashPlanTableProps): ReactElement {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const { data, fetchMore } = useAllCashPlansQuery({
    variables: {
      program: program.id,
      count: rowsPerPage,
    },
    fetchPolicy: 'network-only',
  });
  if (!data) {
    return null;
  }
  let { edges } = data.allCashPlans;
  edges = edges.slice(rowsPerPage * page, rowsPerPage * page + rowsPerPage);
  const cashPlans = edges.map((edge) => edge.node as CashPlanNode);
  /* eslint-disable @typescript-eslint/no-empty-function */
  return (
    <TableComponent<CashPlanNode>
      title='Cash Plans'
      data={cashPlans}
      renderRow={(row) => {
        return (
          <TableRow
            hover
            // onClick={(event) => handleClick(event, row.)}
            role='checkbox'
            key={row.id}
          >
            <TableCell align='left'>{row.cashAssistId}</TableCell>
            <TableCell align='left'>
              <StatusContainer>
                <StatusBox
                  status={row.status}
                  statusToColor={cashPlanStatusToColor}
                />
              </StatusContainer>
            </TableCell>
            <TableCell align='right'>{row.numberOfHouseholds}</TableCell>
            <TableCell align='left'>{row.currency}</TableCell>
            <TableCell align='right'>
              {row.totalEntitledQuantity.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </TableCell>
            <TableCell align='right'>
              {row.totalDeliveredQuantity.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </TableCell>
            <TableCell align='right'>
              {row.totalUndeliveredQuantity.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </TableCell>
            <TableCell align='left'>
              <Moment format='MM/DD/YYYY'>{row.disbursementDate}</Moment>
            </TableCell>
          </TableRow>
        );
      }}
      headCells={headCells}
      rowsPerPageOptions={[5, 10, 15]}
      rowsPerPage={rowsPerPage}
      page={page}
      itemsCount={data.allCashPlans.totalCount}
      handleChangePage={(event, newPage) => {
        if (newPage < page) {
          setPage(newPage);
          return;
        }

        setPage(newPage);
        const after = data.allCashPlans.edges[cashPlans.length - 1].cursor;
        fetchMore({
          variables: {
            after,
            program: program.id,
            count: rowsPerPage,
          },
          updateQuery: (prev, { fetchMoreResult }) => {
            const newData = { ...prev };
            newData.allCashPlans = { ...prev.allCashPlans };
            const newIds = fetchMoreResult.allCashPlans.edges.map(
              ({ node }) => node.id,
            );
            newData.allCashPlans.edges = [
              ...prev.allCashPlans.edges.filter(
                (node) => !newIds.includes(node.node.id),
              ),
              ...fetchMoreResult.allCashPlans.edges,
            ];
            return newData;
          },
        });
      }}
      handleChangeRowsPerPage={(event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
      }}
      handleRequestSort={() => {}}
      orderBy={null}
      order='asc'
    />
  );
}
