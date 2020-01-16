import React, { ReactElement, useState } from 'react';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import {
  CashPlanNode,
  ProgramNode,
  useAllCashPlansQuery,
} from '../__generated__/graphql';
import { TableComponent } from '../components/table/TableComponent';
import { HeadCell } from '../components/table/EnhancedTableHead';

const headCells: HeadCell<CashPlanNode>[] = [
  {
    disablePadding: false,
    label: 'Cash Plan ID',
    id: 'cashAssistId',
    numeric: false,
  },
  // {
  //   disablePadding: false,
  //   label: 'Status',
  //   id: 'cashPlanId',
  //   numeric: false,
  // },
  {
    disablePadding: false,
    label: 'No. of Households',
    id: 'numberOfHouseholds',
    numeric: true,
  },
  // {
  //   disablePadding: false,
  //   label: 'Currency',
  //   id: 'currency',
  //   numeric: false,
  // },
  // {
  //   disablePadding: false,
  //   label: 'Total Entitled Quantity',
  //   id: 'totalEntitledQuantity',
  //   numeric: true,
  // },
  // {
  //   disablePadding: false,
  //   label: 'Total Delivered Quantity',
  //   id: 'totalDeliveredQuantity',
  //   numeric: true,
  // },
  // {
  //   disablePadding: false,
  //   label: 'Total Undelivered Quantity',
  //   id: 'totalUndeliveredQuantity',
  //   numeric: true,
  // },
  {
    disablePadding: false,
    label: 'Dispersion Date',
    id: 'disbursementDate',
    numeric: false,
  },
];
// const StatusContainer = styled.div`
//   width: 120px;
// `;

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
  console.log(
    'data',
    data.allCashPlans,
    data.allCashPlans.edges.length,
    cashPlans,
  );
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
            {/*<TableCell align='left'>*/}
            {/*  <StatusContainer>*/}
            {/*    <StatusBox*/}
            {/*      status='ACTIVE'*/}
            {/*      statusToColor={programStatusToColor}*/}
            {/*    />*/}
            {/*  </StatusContainer>*/}
            {/*</TableCell>*/}
            <TableCell align='right'>{row.numberOfHouseholds}</TableCell>
            {/*<TableCell align='left'>{row.currency}</TableCell>*/}
            {/*<TableCell align='right'>{row.totalEntitledQuantity}</TableCell>*/}
            {/*<TableCell align='right'>{row.totalDeliveredQuantity}</TableCell>*/}
            {/*<TableCell align='right'>{row.totalUndeliveredQuantity}</TableCell>*/}
            <TableCell align='left'>{row.disbursementDate}</TableCell>
          </TableRow>
        );
      }}
      headCells={headCells}
      rowsPerPageOptions={[5, 10, 15]}
      rowsPerPage={rowsPerPage}
      page={page}
      itemsCount={50}
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
            newData.allCashPlans.edges = [
              ...prev.allCashPlans.edges,
              ...fetchMoreResult.allCashPlans.edges,
            ];
            console.log('updateQuery', newData);
            return newData;
          },
        });
      }}
      handleChangeRowsPerPage={(event) =>
        setRowsPerPage(parseInt(event.target.value, 10))
      }
      handleRequestSort={() => {}}
      orderBy={null}
      order='asc'
    />
  );
}
