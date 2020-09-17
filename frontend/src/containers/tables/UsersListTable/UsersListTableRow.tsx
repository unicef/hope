import React from 'react';
import { TableCell, TableRow } from '@material-ui/core';
import { UserNode } from '../../../__generated__/graphql';
import { Missing } from '../../../components/Missing';
import { UniversalMoment } from '../../../components/UniversalMoment';

interface UsersListTableRowProps {
  user: UserNode;
}

export function UsersListTableRow({
  user,
}: UsersListTableRowProps): React.ReactElement {
  return (
    <TableRow key={user.id}>
      <TableCell align='left'>{`${user.firstName} ${user.lastName}`}</TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>{user.email}</TableCell>
      <TableCell align='left'>
        <UniversalMoment>{user.lastLogin}</UniversalMoment>
      </TableCell>
    </TableRow>
  );
}
