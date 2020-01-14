import React, { ReactElement } from 'react';
import { TableComponent } from '../table/TableComponent';
import { HeadCell } from '../table/EnhancedTableHead';
import styled from 'styled-components';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import { StatusBox } from '../StatusBox';
import { programStatusToColor } from '../../utils/utils';
import { LabelizedField } from '../LabelizedField';

interface CashPlan {
  id: string;
  cashPlanId: string;
  status: string;
  householdsCount: number;
  currency: string;
  totalEntitledQuantity: number;
  totalDeliveredQuantity: number;
  totalUndeliveredQuantity: number;
  dispersionDate: string;
}

const data: CashPlan[] = [
  {
    id: '1',
    cashPlanId: '183-19-CSH-00102',
    status: 'active',
    householdsCount: 123,
    currency: 'PHP',
    totalDeliveredQuantity: 112123,
    totalEntitledQuantity: 123123,
    totalUndeliveredQuantity: 123132,
    dispersionDate: '09/01/2020',
  },
  {
    id: '1',
    cashPlanId: '183-19-CSH-00102',
    status: 'active',
    householdsCount: 123,
    currency: 'PHP',
    totalDeliveredQuantity: 112123,
    totalEntitledQuantity: 123123,
    totalUndeliveredQuantity: 123132,
    dispersionDate: '09/01/2020',
  },
  {
    id: '1',
    cashPlanId: '183-19-CSH-00102',
    status: 'active',
    householdsCount: 123,
    currency: 'PHP',
    totalDeliveredQuantity: 112123,
    totalEntitledQuantity: 123123,
    totalUndeliveredQuantity: 123132,
    dispersionDate: '09/01/2020',
  },
  {
    id: '1',
    cashPlanId: '183-19-CSH-00102',
    status: 'active',
    householdsCount: 123,
    currency: 'PHP',
    totalDeliveredQuantity: 112123,
    totalEntitledQuantity: 123123,
    totalUndeliveredQuantity: 123132,
    dispersionDate: '09/01/2020',
  },
];

const headCells: HeadCell<CashPlan>[] = [
  {
    disablePadding: false,
    label: 'Cash Plan ID',
    id: 'cashPlanId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'cashPlanId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'No. of Households',
    id: 'householdsCount',
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
    id: 'dispersionDate',
    numeric: false,
  },
];

const StatusContainer = styled.div`
  width: 120px;
`;


export function CashPlanTable(): ReactElement {
  /* eslint-disable @typescript-eslint/no-empty-function */
  return (
    <TableComponent<CashPlan>
      title='Cash Plans'
      data={data}
      renderRow={(row) => {
        return (
          <TableRow
            hover
            // onClick={(event) => handleClick(event, row.)}
            role='checkbox'
            key={row.id}
          >
            <TableCell align='left'>{row.cashPlanId}</TableCell>
            <TableCell align='left'>
              <StatusContainer>
                <StatusBox
                    status='ACTIVE'
                    statusToColor={programStatusToColor}
                />
              </StatusContainer></TableCell>
            <TableCell align='right'>{row.householdsCount}</TableCell>
            <TableCell align='left'>{row.currency}</TableCell>
            <TableCell align='right'>{row.totalEntitledQuantity}</TableCell>
            <TableCell align='right'>{row.totalDeliveredQuantity}</TableCell>
            <TableCell align='right'>{row.totalUndeliveredQuantity}</TableCell>
            <TableCell align='left'>{row.dispersionDate}</TableCell>
          </TableRow>
        );
      }}
      headCells={headCells}
      rowsPerPageOptions={[5, 10, 15]}
      rowsPerPage={5}
      page={0}
      itemsCount={50}
      handleChangePage={(event) => {}}
      handleChangeRowsPerPage={(event) => {}}
      handleRequestSort={(event, property) => {}}
      orderBy={null}
      order='asc'
    />
  );
}
