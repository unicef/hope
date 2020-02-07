import React, { useState} from 'react';
import styled from "styled-components";
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import { Order, TableComponent } from '../components/table/TableComponent';
import { HeadCell } from '../components/table/EnhancedTableHead';
import {HouseholdNode} from '../__generated__/graphql';

const headCells: HeadCell<HouseholdNode>[] = [
    {
      disablePadding: false,
      label: 'Household ID',
      id: 'householdCaId',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Head of Household',
      id: 'consent',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Household Size',
      id: 'familySize',
      numeric: true,
    },
    {
      disablePadding: false,
      label: 'Location',
      id: 'location',
      numeric: false,
    },
    {
      disablePadding: false,
      label: 'Residence Status',
      id: 'residenceStatus',
      numeric: true,
    },
    {
      disablePadding: false,
      label: 'Total Cash Received',
      id: 'paymentRecords',
      numeric: true,
    },
    {
      disablePadding: false,
      label: 'Registration Date',
      id: 'createdAt',
      numeric: true,
    },
  ];

  const TableWrapper = styled.div`padding: 20px`;

export const HouseholdTable = (): React.ReactElement => {
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const [orderBy, setOrderBy] = useState(null);
    const [orderDirection, setOrderDirection] = useState('asc');

    return (
        <TableWrapper>
        <TableComponent<HouseholdNode> 
        title="Households" 
        page={1}
        data={[]}
        itemsCount={0}
        handleRequestSort={(e) => { console.log(e)}}
        renderRow={(row) => {
        return (
          <TableRow
            hover
            // onClick={(event) => handleClick(event, row.)}
            role='checkbox'
            key={row.id}
          >
            <TableCell align='left'>{row.householdCaId}</TableCell>
            <TableCell align='left'>{row.consent}</TableCell>
            <TableCell align='left'>{row.familySize}</TableCell>
            <TableCell align='left'>{row.location}</TableCell>
            <TableCell align='left'>{row.residenceStatus}</TableCell>
            <TableCell align='left'>{row.paymentRecords}</TableCell>
            <TableCell align='left'>{row.createdAt}</TableCell>
 
          </TableRow>
        );
      }} 
      handleChangeRowsPerPage={(e) => {console.log(e)}}
      handleChangePage={(e) => {console.log(e)}}
      headCells={headCells}
      rowsPerPageOptions={[5, 10, 15]}
      rowsPerPage={rowsPerPage}
      orderBy={orderBy}
      order={orderDirection as Order}/></TableWrapper>)
}