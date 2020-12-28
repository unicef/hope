import React from 'react';
import styled from 'styled-components';
import { TableCell, TableRow } from '@material-ui/core';
import { useHistory } from 'react-router-dom';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { Missing } from '../../../components/Missing';

export const MainActivityLogTableRow = ({ log }) => {
  const businessArea = useBusinessArea();
  const history = useHistory();

  return (
    <TableRow hover role='checkbox' key={log.id}>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
    </TableRow>
  );
};
