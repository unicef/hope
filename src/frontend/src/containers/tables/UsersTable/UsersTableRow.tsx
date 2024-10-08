import * as React from 'react';
import { useState } from 'react';
import styled from 'styled-components';
import TableCell from '@mui/material/TableCell';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import { Box, Collapse, IconButton, TableRow } from '@mui/material';
import { UserNode } from '@generated/graphql';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { StatusBox } from '@components/core/StatusBox';
import { userStatusToColor } from '@utils/utils';

const GreyText = styled.p`
  color: #959698;
`;
interface UsersTableRowProps {
  user: UserNode;
}

export const UsersTableRow = ({
  user,
}: UsersTableRowProps): React.ReactElement => {
  const [open, setOpen] = useState(false);

  const mappedRoles = user?.userRoles?.map((el) => (
    <p key={el.role.name}>
      {el.businessArea.name} / {el.role.name}
    </p>
  ));

  const mappedPartnerRoles = user?.partnerRoles?.map((el) =>
    el.roles.map((role) => (
      <p key={role.name}>
        {el.businessArea.name} / {role.name}
      </p>
    )),
  );

  return (
    <>
      <TableRow key={user.id}>
        <TableCell>
          <IconButton
            data-cy="arrow-down"
            aria-label="expand row"
            size="medium"
            onClick={() => setOpen(!open)}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell
          style={{ width: '300px' }}
          align="left"
        >{`${user.firstName} ${user.lastName}`}</TableCell>
        <TableCell align="left">
          <StatusBox status={user.status} statusToColor={userStatusToColor} />
        </TableCell>
        <TableCell align="left">{user.partner?.name || '-'}</TableCell>
        <TableCell align="left">{user.email}</TableCell>
        <TableCell align="left">
          <UniversalMoment>{user.lastLogin}</UniversalMoment>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={1}>
          <Collapse in={open} timeout="auto" unmountOnExit />
        </TableCell>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={2}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box margin={1} data-cy="country-role">
              <GreyText>Country / Role</GreyText>
            </Box>
            <Box margin={1} data-cy="mapped-country-role">
              {mappedRoles.length ? mappedRoles : 'No roles assigned.'}
            </Box>
            {mappedPartnerRoles.length > 0 && (
              <>
                <Box margin={1} data-cy="partner-role">
                  <GreyText>Partner Roles</GreyText>
                </Box>
                <Box margin={1} data-cy="mapped-partner-role">{mappedPartnerRoles}</Box>
              </>
            )}
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
};
