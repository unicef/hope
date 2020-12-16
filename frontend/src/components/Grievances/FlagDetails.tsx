import {
  Box,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
  makeStyles,
} from '@material-ui/core';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import React, { useState } from 'react';
import { GrievanceTicketQuery } from '../../__generated__/graphql';
import { ConfirmationDialog } from '../ConfirmationDialog';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { Missing } from '../Missing';
import { Flag } from '../Flag';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function FlagDetails({
  ticket,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}): React.ReactElement {
  const [isFlagConfirmed, setFlagConfirmed] = useState(false);
  const useStyles = makeStyles(() => ({
    table: {
      minWidth: 100,
    },
  }));
  const classes = useStyles();
  const businessArea = useBusinessArea();
  const confirmationText =
    'Are you sure you want to confirm flag (sanction list match) ?';
  const removalText = 'Are you sure you want to remove the flag ?';
  return (
    <StyledBox>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>Flag Details</Typography>
          <Box>
            <Button
              component={Link}
              to={`/${businessArea}/grievance-and-feedback`}
              color='primary'
            >
              VIEW SANCTION LIST
            </Button>
            <ConfirmationDialog
              title='Confirmation'
              content={isFlagConfirmed ? removalText : confirmationText}
            >
              {(confirm) => (
                <Button
                  onClick={confirm(() => setFlagConfirmed(!isFlagConfirmed))}
                  variant='outlined'
                  color='primary'
                >
                  {isFlagConfirmed ? 'REMOVE FLAG' : 'CONFIRM FLAG'}
                </Button>
              )}
            </ConfirmationDialog>
          </Box>
        </Box>
      </Title>
      <Table className={classes.table}>
        <TableHead>
          <TableRow>
            <TableCell align='left' />
            <TableCell align='left'>Ref. No. on Sanction List</TableCell>
            <TableCell align='left'>Full Name</TableCell>
            <TableCell align='left'>Date of Birth</TableCell>
            <TableCell align='left'>National Ids</TableCell>
            <TableCell align='left'>Source</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableCell align='left'>{isFlagConfirmed ? <Flag /> : '-'}</TableCell>
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
        </TableBody>
      </Table>
    </StyledBox>
  );
}
