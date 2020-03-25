import React from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import styled from 'styled-components';

export interface ApproveCandidateListPropTypes {
  open: boolean;
  setOpen: Function;
}

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

export function ApproveCandidateList({ open, setOpen }) {
  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll='paper'
      aria-labelledby='form-dialog-title'
    >
      <DialogTitleWrapper>
        <DialogTitle id='scroll-dialog-title'>
          <Typography variant='h6'>Approve Candidate List</Typography>
        </DialogTitle>
      </DialogTitleWrapper>
      <DialogContent>
        <DialogDescription>
          Are you sure you want to approve the targeting criteria for this
          Candidate List? Once a Candidate List is <strong>Approved</strong> the
          targeting criteria will be permanently frozen.
        </DialogDescription>
        <DialogDescription>
          Please select a Programme you would like to associate this candidate
          list with:
        </DialogDescription>
      </DialogContent>
      <DialogFooter>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>CANCEL</Button>
          <Button type='submit' color='primary' variant='contained'>
            Approve
          </Button>
        </DialogActions>
      </DialogFooter>
    </Dialog>
  );
}
