import React, { ReactElement } from 'react';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import { CashPlanNode, ProgramNode } from '../__generated__/graphql';
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
  const cashPlans = program.cashPlans.edges.map((edge) => edge.node);
  /* eslint-disable @typescript-eslint/no-empty-function */
  return (
    <TableComponent<CashPlanNode>
      title='Cash Plans'
      data={cashPlans}
      renderRow={(row ) => {
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
      rowsPerPage={5}
      page={0}
      itemsCount={50}
      handleChangePage={() => {}}
      handleChangeRowsPerPage={() => {}}
      handleRequestSort={() => {}}
      orderBy={null}
      order='asc'
    />
  );
}
