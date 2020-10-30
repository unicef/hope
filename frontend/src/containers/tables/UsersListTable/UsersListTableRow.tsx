import React, { useState } from 'react';
import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import KeyboardArrowDownIcon from '@material-ui/icons/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@material-ui/icons/KeyboardArrowUp';
import { Box, Collapse, IconButton, TableRow } from '@material-ui/core';
import { UserNode } from '../../../__generated__/graphql';
import { UniversalMoment } from '../../../components/UniversalMoment';
import { StatusBox } from '../../../components/StatusBox';
import { userStatusToColor } from '../../../utils/utils';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

const GreyText = styled.p`
  color: #959698;
`;
interface UsersListTableRowProps {
  user: UserNode;
}

export function UsersListTableRow({
  user,
}: UsersListTableRowProps): React.ReactElement {
  const [open, setOpen] = useState(false);

  const mappedRoles = user?.userRoles?.map((el) => (
    <p>
      {el.businessArea.name} / {el.role.name}
    </p>
  ));
  return (
    <>
      <TableRow key={user.id}>
        <TableCell>
          <IconButton
            aria-label='expand row'
            size='small'
            onClick={() => setOpen(!open)}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell align='left'>{`${user.firstName} ${user.lastName}`}</TableCell>
        <TableCell align='left'>
          <StatusContainer>
            <StatusBox status={user.status} statusToColor={userStatusToColor} />
          </StatusContainer>
        </TableCell>
        <TableCell align='left'>{user.partner}</TableCell>
        <TableCell align='left'>{user.email}</TableCell>
        <TableCell align='left'>
          {user.lastLogin ? (
            <UniversalMoment>{user.lastLogin}</UniversalMoment>
          ) : (
            '-'
          )}
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={1}>
          <Collapse in={open} timeout='auto' unmountOnExit />
        </TableCell>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={2}>
          <Collapse in={open} timeout='auto' unmountOnExit>
            <Box margin={1}>
              <GreyText>Country / Role</GreyText>
            </Box>
            <Box margin={1}>
              {mappedRoles.length ? mappedRoles : 'No roles assigned.'}
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
}
